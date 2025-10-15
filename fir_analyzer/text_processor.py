"""
Bilingual Text Processor for FIR Analysis
=========================================

Handles mixed English-Telugu text processing, language detection,
and text normalization for accurate information extraction.
"""

import re
import spacy
from typing import Dict, List, Tuple, Optional
from deep_translator import GoogleTranslator
import unicodedata


class BilingualTextProcessor:
    """Processes mixed English-Telugu FIR text for analysis."""
    
    def __init__(self):
        self.translator = GoogleTranslator
        self.nlp = spacy.load("en_core_web_sm")
        
        # Telugu Unicode ranges
        self.telugu_pattern = re.compile(r'[\u0C00-\u0C7F]+')
        
        # Common Telugu legal terms
        self.telugu_legal_terms = {
            'సంఘటన': 'incident',
            'అభియోగం': 'complaint',
            'అపరాధం': 'offence',
            'ఆరోపణ': 'allegation',
            'సాక్షి': 'witness',
            'అనుమానితుడు': 'accused',
            'అత్యాచారం': 'atrocity',
            'హింస': 'violence',
            'దోపిడీ': 'robbery',
            'చాకిరీ': 'theft'
        }
        
        # English legal patterns
        self.english_patterns = {
            'date': r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
            'time': r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b',
            'age': r'\b(?:aged|age)\s*(\d{1,2})\s*(?:years?)?\b',
            'amount': r'₹\s*[\d,]+(?:\.\d{2})?',
            'vehicle_number': r'[A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4}',
            'phone_number': r'\b\d{10}\b'
        }
        
        # Telugu patterns
        self.telugu_patterns = {
            'age': r'(\d{1,2})\s*సంవత్సరాల\s*వయస్సు',
            'amount': r'₹\s*[\d,]+',
            'date': r'\d{1,2}-\d{1,2}-\d{4}'
        }
    
    def detect_language_mix(self, text: str) -> Dict[str, float]:
        """Detect the language composition of the text."""
        telugu_chars = len(self.telugu_pattern.findall(text))
        total_chars = len(text.replace(' ', ''))
        
        telugu_ratio = telugu_chars / total_chars if total_chars > 0 else 0
        english_ratio = 1 - telugu_ratio
        
        return {
            'telugu_ratio': telugu_ratio,
            'english_ratio': english_ratio,
            'is_mixed': 0.1 < telugu_ratio < 0.9,
            'primary_language': 'telugu' if telugu_ratio > 0.5 else 'english'
        }
    
    def normalize_text(self, text: str) -> str:
        """Normalize and clean the input text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Normalize Unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Fix common OCR errors
        text = text.replace('|', 'I').replace('0', 'O')
        
        return text
    
    def extract_telugu_terms(self, text: str) -> Dict[str, str]:
        """Extract and translate Telugu legal terms."""
        found_terms = {}
        
        for telugu_term, english_term in self.telugu_legal_terms.items():
            if telugu_term in text:
                found_terms[telugu_term] = english_term
        
        return found_terms
    
    def translate_telugu_sections(self, text: str) -> str:
        """Translate Telugu sections to English for processing."""
        telugu_sections = self.telugu_pattern.findall(text)
        
        for section in telugu_sections:
            try:
                translation = self.translator(source='te', target='en').translate(section)
                text = text.replace(section, f"{section} ({translation})")
            except:
                continue
        
        return text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from the text."""
        # Process with spaCy
        doc = self.nlp(text)
        
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'times': [],
            'amounts': [],
            'vehicles': []
        }
        
        # Extract using spaCy NER
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'GPE' or ent.label_ == 'LOC':
                entities['locations'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'TIME':
                entities['times'].append(ent.text)
        
        # Extract using regex patterns
        for pattern_name, pattern in self.english_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if pattern_name == 'amount':
                entities['amounts'].extend(matches)
            elif pattern_name == 'vehicle_number':
                entities['vehicles'].extend(matches)
        
        # Extract Telugu patterns
        for pattern_name, pattern in self.telugu_patterns.items():
            matches = re.findall(pattern, text)
            if pattern_name == 'amount':
                entities['amounts'].extend([f"₹{match}" for match in matches])
        
        return entities
    
    def segment_text(self, text: str) -> Dict[str, str]:
        """Segment FIR text into logical sections."""
        segments = {
            'header': '',
            'complainant_info': '',
            'incident_description': '',
            'accused_details': '',
            'witnesses': '',
            'evidence': '',
            'impact': ''
        }
        
        # Simple segmentation based on keywords
        lines = text.split('\n')
        current_section = 'incident_description'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers
            if any(keyword in line.lower() for keyword in ['complainant', 'reported', 'informant']):
                current_section = 'complainant_info'
            elif any(keyword in line.lower() for keyword in ['accused', 'suspect', 'perpetrator']):
                current_section = 'accused_details'
            elif any(keyword in line.lower() for keyword in ['witness', 'seen', 'observed']):
                current_section = 'witnesses'
            elif any(keyword in line.lower() for keyword in ['evidence', 'weapon', 'vehicle']):
                current_section = 'evidence'
            elif any(keyword in line.lower() for keyword in ['impact', 'injury', 'damage', 'loss']):
                current_section = 'impact'
            
            segments[current_section] += line + ' '
        
        return segments
    
    def process_fir_text(self, text: str) -> Dict:
        """Main processing function for FIR text with enhanced bilingual support."""
        # Normalize text
        normalized_text = self.normalize_text(text)
        
        # Detect language mix
        language_info = self.detect_language_mix(normalized_text)
        
        # Enhanced bilingual processing
        processed_text = self.enhanced_bilingual_processing(normalized_text)
        
        # Extract entities with improved accuracy
        entities = self.extract_entities(processed_text)
        
        # Extract Telugu terms
        telugu_terms = self.extract_telugu_terms(normalized_text)
        
        # Segment text
        segments = self.segment_text(processed_text)
        
        return {
            'original_text': text,
            'normalized_text': normalized_text,
            'processed_text': processed_text,
            'language_info': language_info,
            'entities': entities,
            'telugu_terms': telugu_terms,
            'segments': segments
        }
    
    def enhanced_bilingual_processing(self, text: str) -> str:
        """Enhanced processing for mixed English-Telugu text."""
        processed_text = text
        
        # Step 1: Translate Telugu sections
        processed_text = self.translate_telugu_sections(processed_text)
        
        # Step 2: Clean and standardize mixed text
        processed_text = self.clean_mixed_text(processed_text)
        
        # Step 3: Extract and preserve legal terms
        processed_text = self.preserve_legal_terms(processed_text)
        
        return processed_text
    
    def clean_mixed_text(self, text: str) -> str:
        """Clean and standardize mixed language text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common OCR errors
        text = text.replace('|', 'I').replace('0', 'O')
        
        # Standardize date formats
        text = re.sub(r'(\d{1,2})(?:st|nd|rd|th)', r'\1', text)
        
        # Standardize time formats
        text = re.sub(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)', r'\1:\2 \3', text)
        
        return text
    
    def preserve_legal_terms(self, text: str) -> str:
        """Preserve important legal terms during processing."""
        # List of important legal terms to preserve
        legal_terms = [
            'Scheduled Caste', 'Scheduled Tribe', 'SC', 'ST',
            'Agricultural labourer', 'History-sheeter',
            'brother-in-law', 'sarpanch', 'village',
            'country-made pistol', 'motorbike', 'bicycle',
            'weekly shandy', 'culvert', 'mandal'
        ]
        
        # Ensure these terms are preserved in their original form
        for term in legal_terms:
            if term.lower() in text.lower():
                # Find and preserve the exact case
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                text = pattern.sub(term, text)
        
        return text
