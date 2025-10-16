"""
FIR Analysis System
==================

A comprehensive system for analyzing First Information Reports (FIRs)
with bilingual text processing and legal section mapping.

Modules:
- text_processor: Bilingual text processing
- information_extractor: Structured data extraction
- legal_mapper: Legal section mapping
- web_researcher: Real-time legal updates
- fir_validator: Output validation
"""

__version__ = "1.0.0"
__author__ = "Project Dharma Team"

from .text_processor import BilingualTextProcessor
from .information_extractor import FIRInformationExtractor
from .legal_mapper import LegalSectionMapper
from .web_researcher import LegalWebResearcher
from .fir_validator import FIRValidator
from .main_analyzer import FIRAnalyzer

__all__ = [
    "BilingualTextProcessor",
    "FIRInformationExtractor", 
    "LegalSectionMapper",
    "LegalWebResearcher",
    "FIRValidator",
    "FIRAnalyzer"
]
