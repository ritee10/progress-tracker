import pytest
from app.services.pdf_parser_service import PdfParserService

def test_parse_hierarchy_simple():
    service = PdfParserService(db=None)
    text = """
    1 Introduction
    1.1 What is AI
    1.1.1 History
    1.2 ML
    2 Deep Learning
    """
    
    topics = service.parse_hierarchy_from_text(text)
    
    assert len(topics) == 5
    assert topics[0]["number"] == "1"
    assert topics[0]["title"] == "Introduction"
    assert topics[0]["depth"] == 1
    
    assert topics[1]["number"] == "1.1"
    assert topics[1]["title"] == "What is AI"
    assert topics[1]["depth"] == 2
    
    assert topics[2]["number"] == "1.1.1"
    assert topics[2]["title"] == "History"
    assert topics[2]["depth"] == 3
    
    assert topics[3]["number"] == "1.2"
    assert topics[3]["title"] == "ML"
    assert topics[3]["depth"] == 2

def test_parse_hierarchy_removes_duplicates():
    service = PdfParserService(db=None)
    # Simulates TOC vs Actual Body pages
    text = """
    1 Introduction
    1 Introduction
    1.1 AI
    1.1 AI
    """
    topics = service.parse_hierarchy_from_text(text)
    assert len(topics) == 2

def test_parse_hierarchy_ignores_garbage():
    service = PdfParserService(db=None)
    text = """
    This is some preamble
    1 Intro
    Just a random paragraph
    1.1 Details
    Page 12
    """
    topics = service.parse_hierarchy_from_text(text)
    assert len(topics) == 2
    assert topics[0]["number"] == "1"
    assert topics[1]["number"] == "1.1"
