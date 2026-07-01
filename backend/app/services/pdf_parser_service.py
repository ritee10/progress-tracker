# ============================================================
# Service — PDF Parser & Preview Editor
# ============================================================

import io
import re
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

import pypdf
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.import_job import PdfImportJob
from app.models.topic import Topic
from app.utils.date_utils import utc_now

logger = logging.getLogger(__name__)

class PdfParserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        pdf_file = io.BytesIO(file_bytes)
        try:
            reader = pypdf.PdfReader(pdf_file)
            text_chunks = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)
            return "\n".join(text_chunks)
        except Exception as e:
            logger.error(f"Failed to read PDF: {e}")
            raise ValueError("Corrupted or unreadable PDF file")

    def parse_hierarchy_from_text(self, text: str) -> List[Dict]:
        lines = text.split("\n")
        topics = []
        pattern = re.compile(r"^\s*(\d+(?:\.\d+)*)[\s]+(.+)$")
        seen_numbers = set()
        
        for line in lines:
            line = line.strip()
            if not line: continue
            match = pattern.match(line)
            if match:
                number_str = match.group(1)
                title = match.group(2).strip()
                if number_str in seen_numbers:
                    continue
                seen_numbers.add(number_str)
                depth = len(number_str.split("."))
                topics.append({
                    "number": number_str,
                    "title": title,
                    "depth": depth
                })
        return topics

    def build_preview_tree(self, parsed_nodes: List[Dict]) -> List[Dict]:
        """Builds a flat list of nodes with UUIDs and parent relationships for preview."""
        active_parents: Dict[int, Dict] = {}
        tree_nodes = []
        
        for idx, node in enumerate(parsed_nodes):
            topic_id = str(uuid.uuid4())
            depth = node["depth"]
            
            parent = active_parents.get(depth - 1)
            parent_id = parent["id"] if parent else None
            
            t = {
                "id": topic_id,
                "parent_id": parent_id,
                "title": node["title"],
                "number": node["number"],
                "depth": depth,
                "order_index": idx + 1
            }
            
            active_parents[depth] = t
            keys_to_clear = [k for k in active_parents.keys() if k > depth]
            for k in keys_to_clear:
                del active_parents[k]
                
            tree_nodes.append(t)
            
        return tree_nodes

    async def execute_import_job(self, job_id: uuid.UUID, file_bytes: bytes) -> None:
        """Parses the PDF and saves the preview JSON to the job tracker."""
        stmt = select(PdfImportJob).where(PdfImportJob.id == job_id)
        job = (await self.db.execute(stmt)).scalar_one_or_none()
        if not job: return
            
        try:
            job.status = "processing"
            await self.db.flush()
            
            text = self.extract_text_from_pdf(file_bytes)
            parsed_nodes = self.parse_hierarchy_from_text(text)
            job.total_topics = len(parsed_nodes)
            
            if len(parsed_nodes) > 0:
                tree_data = self.build_preview_tree(parsed_nodes)
                job.tree_data = tree_data
                job.status = "preview"
            else:
                job.status = "completed"
                
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            job = (await self.db.execute(stmt)).scalar_one_or_none()
            if job:
                job.status = "failed"
                job.error_message = str(e)
                job.completed_at = utc_now()
                await self.db.commit()
            logger.error(f"PDF Import Job {job_id} failed: {e}")

    # ── Preview Editor Mutators ───────────────────────────────────────

    def validate_preview_tree(self, tree_data: List[Dict]) -> List[str]:
        """Returns a list of error strings if invalid."""
        errors = []
        node_map = {n["id"]: n for n in tree_data}
        
        # Check orphans & cycles
        for node in tree_data:
            if not node.get("title") or not node["title"].strip():
                errors.append(f"Node {node['id']} has empty title.")
            
            parent_id = node.get("parent_id")
            if parent_id and parent_id not in node_map:
                errors.append(f"Node {node['title']} references missing parent {parent_id}.")
                continue
                
            # Cycle detection
            visited = set()
            curr = node
            while curr.get("parent_id"):
                curr_id = curr["parent_id"]
                if curr_id in visited or curr_id == node["id"]:
                    errors.append(f"Circular hierarchy detected at node {node['title']}.")
                    break
                visited.add(curr_id)
                curr = node_map.get(curr_id)
                if not curr: break
                
        return errors

    async def commit_import_session(self, job_id: uuid.UUID) -> None:
        """Takes the final tree_data, builds Topic models, and saves them."""
        stmt = select(PdfImportJob).where(PdfImportJob.id == job_id)
        job = (await self.db.execute(stmt)).scalar_one_or_none()
        
        if not job or job.status != "preview":
            raise HTTPException(status_code=400, detail="Invalid job or status for commit.")
            
        tree_data = job.tree_data or []
        errors = self.validate_preview_tree(tree_data)
        if errors:
            raise HTTPException(status_code=400, detail=f"Validation failed: {', '.join(errors)}")
            
        node_map = {n["id"]: n for n in tree_data}
        
        # Calculate full paths and depths based on the final hierarchy structure
        # (Users might have moved things, so the JSON depth/paths could be dirty)
        def get_path_and_depth(node_id: str) -> tuple[str, int, int]:
            path_parts = []
            curr = node_map[node_id]
            while curr:
                path_parts.insert(0, curr["id"])
                p_id = curr.get("parent_id")
                curr = node_map.get(p_id) if p_id else None
            
            # depth is number of parents (path length - 1)
            depth = len(path_parts) - 1
            path = "/" + "/".join(path_parts)
            level = depth
            return path, depth, level
            
        topics = []
        for node in tree_data:
            path, depth, level = get_path_and_depth(node["id"])
            t = Topic(
                id=uuid.UUID(node["id"]),
                user_id=job.user_id,
                skill_id=job.skill_id,
                parent_id=uuid.UUID(node["parent_id"]) if node.get("parent_id") else None,
                title=node["title"],
                description=f"Imported from PDF section {node.get('number', '')}",
                order_index=node.get("order_index", 0),
                level=level,
                path=path,
                depth=depth,
                is_root=(node.get("parent_id") is None),
            )
            topics.append(t)
            
        try:
            self.db.add_all(topics)
            job.created_topics = len(topics)
            job.status = "completed"
            job.completed_at = utc_now()
            
            # Log Activity
            from app.models.activity import ActivityLog
            log = ActivityLog(
                user_id=job.user_id,
                activity_type="PDF_IMPORTED",
                entity_id=job.skill_id,
                metadata_json={"filename": job.filename, "topics_created": len(topics)}
            )
            self.db.add(log)
            
            # Clear tree_data to save space? Up to biz logic. Let's keep it for history.
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
