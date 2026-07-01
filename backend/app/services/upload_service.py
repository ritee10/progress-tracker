import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from supabase import create_client, Client

from app.core.config import get_settings

settings = get_settings()

class UploadService:
    def __init__(self):
        if settings.SUPABASE_URL and settings.SUPABASE_KEY:
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        else:
            self.supabase = None
        self.bucket_name = settings.STORAGE_BUCKET_UPLOADS

    async def upload_pdf(self, file: UploadFile, user_id: str) -> str:
        """
        Uploads a PDF file to Supabase Storage and returns the public URL or file path.
        """
        if not self.supabase:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service not configured (Supabase credentials missing)."
            )

        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed."
            )

        file_extension = "pdf"
        unique_filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
        
        file_bytes = await file.read()
        
        try:
            # Upload to Supabase Storage
            response = self.supabase.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )
            return unique_filename
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to storage: {str(e)}"
            )

    def get_public_url(self, file_path: str) -> str:
        """
        Retrieves the public URL for a given file path in the bucket.
        """
        if not self.supabase:
            return ""
        try:
            return self.supabase.storage.from_(self.bucket_name).get_public_url(file_path)
        except Exception:
            return ""

    def delete_file(self, file_path: str) -> bool:
        """
        Deletes a file from Supabase Storage.
        """
        if not self.supabase:
            return False
        try:
            self.supabase.storage.from_(self.bucket_name).remove([file_path])
            return True
        except Exception:
            return False

upload_service = UploadService()
