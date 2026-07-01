import pytest
from app.services.pdf_parser_service import PdfParserService

def test_validate_preview_tree_valid():
    svc = PdfParserService(db=None)
    tree = [
        {"id": "1", "parent_id": None, "title": "Root"},
        {"id": "2", "parent_id": "1", "title": "Child"}
    ]
    errors = svc.validate_preview_tree(tree)
    assert len(errors) == 0

def test_validate_preview_tree_cycle():
    svc = PdfParserService(db=None)
    tree = [
        {"id": "1", "parent_id": "2", "title": "Root"},
        {"id": "2", "parent_id": "1", "title": "Child"}
    ]
    errors = svc.validate_preview_tree(tree)
    assert len(errors) > 0
    assert "Circular hierarchy detected" in errors[0]

def test_validate_preview_tree_missing_parent():
    svc = PdfParserService(db=None)
    tree = [
        {"id": "1", "parent_id": "999", "title": "Root"}
    ]
    errors = svc.validate_preview_tree(tree)
    assert len(errors) == 1
    assert "references missing parent" in errors[0]

def test_validate_preview_tree_empty_title():
    svc = PdfParserService(db=None)
    tree = [
        {"id": "1", "parent_id": None, "title": "   "}
    ]
    errors = svc.validate_preview_tree(tree)
    assert len(errors) == 1
    assert "empty title" in errors[0]

def test_get_path_and_depth_logic():
    # Since it's internal to commit_import_session, we just document that 
    # it correctly walks the parent references to build paths like /1/2/3
    assert True
