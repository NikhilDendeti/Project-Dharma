"""
Main FIR Analyzer
================

Integrates all FIR analysis components to provide comprehensive
analysis of First Information Reports with legal mapping.
"""

from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import os
from openai import OpenAI

from .text_processor import BilingualTextProcessor
from .information_extractor import FIRInformationExtractor
from .legal_mapper import LegalSectionMapper
from .web_researcher import LegalWebResearcher
from .fir_validator import FIRValidator


class FIRAnalyzer:
    """Main FIR analysis system that integrates all components with OpenAI chat completion."""
    
    def __init__(self):
        self.text_processor = BilingualTextProcessor()
        self.information_extractor = FIRInformationExtractor()
        self.legal_mapper = LegalSectionMapper()
        self.web_researcher = LegalWebResearcher()
        self.validator = FIRValidator()
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    def analyze_fir(self, fir_text: str, include_web_research: bool = True) -> Dict[str, Any]:
        """
        Perform comprehensive FIR analysis using OpenAI chat completion for enhanced accuracy.
        
        Args:
            fir_text: Raw FIR text (English/Telugu/Mixed)
            include_web_research: Whether to include web research
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Step 1: Process text with enhanced bilingual support
            processed_text = self.text_processor.process_fir_text(fir_text)
            
            # Step 2: Use OpenAI chat completion for enhanced information extraction
            extracted_info = self._enhanced_extraction_with_openai(
                processed_text['processed_text'], 
                fir_text
            )
            
            # Step 3: Map to legal sections
            offences_list = extracted_info.get('Offences', [])
            legal_mappings = self.legal_mapper.map_offences_to_sections(offences_list)
            
            # Step 4: Generate legal summary
            legal_summary = self.legal_mapper.generate_legal_summary(
                extracted_info, legal_mappings
            )
            
            # Step 5: Validate information
            validation_report = self.validator.generate_validation_report(extracted_info)
            
            # Step 6: Web research (optional)
            web_research = {}
            if include_web_research:
                web_research = self._perform_web_research(legal_summary)
            
            # Step 7: Generate final report
            final_report = self._generate_final_report(
                processed_text,
                extracted_info,
                legal_mappings,
                legal_summary,
                validation_report,
                web_research
            )
            
            return final_report
            
        except Exception as e:
            return {
                'error': True,
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _enhanced_extraction_with_openai(self, processed_text: str, original_text: str) -> Dict[str, Any]:
        """Use OpenAI chat completion for enhanced information extraction with exact format specification."""
        try:
            prompt = f"""
            You are a legal expert analyzing a First Information Report (FIR) written in mixed English-Telugu text. 
            Your task is to extract information in the EXACT format specified below with perfect accuracy.

            IMPORTANT INSTRUCTIONS:
            1. The text may contain both English and Telugu languages - handle both correctly
            2. Extract information with 100% accuracy from the provided text
            3. Use the EXACT field names and structure provided below
            4. For missing information, use "N/A" or appropriate default values
            5. Return ONLY valid JSON, no additional text or explanations

            FIR Text to Analyze:
            {original_text}

            REQUIRED OUTPUT FORMAT (EXACT JSON STRUCTURE):
            {{
              "Complainant": {{
                "Name": "extract full name of complainant",
                "Father": "extract father's name (S/o format)",
                "Age": "extract age as integer number",
                "Community": "extract caste/community (e.g., Scheduled Caste, SC, ST, etc.)",
                "Occupation": "extract occupation/profession",
                "Address": "extract complete address including village, mandal, etc."
              }},
              "DateTime": "extract date and time in format DD-MM-YYYY, HH:MM AM/PM",
              "Place": "extract exact incident location/place",
              "Accused": [
                {{
                  "Name": "extract accused person's name",
                  "Age": "extract age as integer",
                  "Relation": "extract relation (e.g., S/o, brother-in-law, etc.)",
                  "History": "extract criminal history if mentioned (e.g., History-sheeter)",
                  "Occupation": "extract occupation if mentioned",
                  "Address": "extract address if mentioned"
                }}
              ],
              "Vehicles": ["extract vehicle numbers with descriptions (e.g., AP-37-BX-4321 (Red Pulsar))"],
              "WeaponsUsed": ["extract all weapons mentioned (e.g., Country-made pistol, Stick)"],
              "Offences": ["extract all offences committed (e.g., Caste abuse, Robbery, Assault)"],
              "Injuries": "extract injury details (e.g., Bleeding injury on left arm)",
              "PropertyLoss": ["extract stolen items with values (e.g., Samsung mobile phone worth ₹15,000)"],
              "Threats": ["extract all threats made (e.g., Kill him, Set fire to his hut)"],
              "Witnesses": ["extract all witness names"],
              "Impact": "extract impact/effect of incident (e.g., Fear, public fled, complainant hospitalized)"
            }}

            SAMPLE EXPECTED OUTPUT FOR REFERENCE:
            {{
              "Complainant": {{
                "Name": "Rajesh Kumar",
                "Father": "Venkat Rao",
                "Age": 34,
                "Community": "Scheduled Caste",
                "Occupation": "Agricultural labourer",
                "Address": "Gollapadu village, Bhimavaram Mandal"
              }},
              "DateTime": "14-09-2025, 8:15 PM",
              "Place": "Narsapur Road culvert, Bhimavaram",
              "Accused": [
                {{"Name": "Ramesh Babu", "Age": 28, "Relation": "S/o Narayana", "History": "History-sheeter", "Occupation": "N/A", "Address": "Gollapadu"}},
                {{"Name": "Srinivas", "Age": 30, "Relation": "Brother-in-law of sarpanch", "History": "N/A", "Occupation": "N/A", "Address": "N/A"}},
                {{"Name": "Murali Krishna", "Age": 32, "Relation": "N/A", "History": "N/A", "Occupation": "Driver", "Address": "Mogaltur"}},
                {{"Name": "Unknown", "Age": "N/A", "Relation": "N/A", "History": "N/A", "Occupation": "N/A", "Address": "N/A"}}
              ],
              "Vehicles": ["AP-37-BX-4321 (Red Pulsar)", "AP-37-CQ-9187 (Black Splendor)"],
              "WeaponsUsed": ["Country-made pistol", "Stick"],
              "Offences": ["Caste abuse", "Threat with firearm", "Robbery", "Assault causing injury"],
              "Injuries": "Bleeding injury on left arm",
              "PropertyLoss": ["Samsung mobile phone worth ₹15,000", "Cash ₹12,500"],
              "Threats": ["Kill him", "Set fire to his hut"],
              "Witnesses": ["Suresh", "Koteswara Rao", "Lakshmi"],
              "Impact": "Fear, public fled, complainant hospitalized"
            }}

            CRITICAL REQUIREMENTS:
            - Extract information ONLY from the provided FIR text
            - Use exact field names as specified above
            - Handle both English and Telugu text correctly
            - For multiple accused persons, create separate objects in the array
            - For missing information, use "N/A" or appropriate defaults
            - Ensure all extracted data is accurate and complete
            - Return ONLY the JSON object, no markdown formatting or additional text

            Now extract the information from the provided FIR text in the exact format above:
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a legal expert specializing in First Information Report (FIR) analysis. 
                        Your expertise includes:
                        - Analyzing mixed English-Telugu legal documents
                        - Extracting structured information with 100% accuracy
                        - Understanding Indian legal terminology and formats
                        - Processing bilingual text with cultural context
                        - Following exact JSON format specifications
                        
                        CRITICAL: You must return ONLY valid JSON in the exact format specified. 
                        No markdown, no explanations, no additional text."""
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=3000
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            
            # Clean the response to extract JSON
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            elif result_text.startswith('```'):
                result_text = result_text[3:]
            
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            # Remove any leading/trailing whitespace
            result_text = result_text.strip()
            
            # Try to find JSON object boundaries
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx + 1]
            
            # Parse JSON with error handling
            try:
                extracted_info = json.loads(result_text)
                
                # Validate that we have the expected structure
                required_fields = ['Complainant', 'DateTime', 'Place', 'Accused', 'Vehicles', 
                                 'WeaponsUsed', 'Offences', 'Injuries', 'PropertyLoss', 
                                 'Threats', 'Witnesses', 'Impact']
                
                for field in required_fields:
                    if field not in extracted_info:
                        print(f"Warning: Missing field '{field}' in extracted information")
                        extracted_info[field] = "N/A" if field != 'Accused' else []
                
                return extracted_info
                
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {result_text}")
                raise e
            
        except Exception as e:
            print(f"OpenAI extraction failed, falling back to traditional method: {e}")
            # Fallback to traditional extraction
            return self.information_extractor.extract_all_information(processed_text)
    
    def _perform_web_research(self, legal_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web research for legal updates and precedents."""
        web_research = {
            'legal_updates': [],
            'case_precedents': [],
            'section_validity': {},
            'judicial_guidelines': []
        }
        
        try:
            # Get legal sections for research
            legal_sections = legal_summary.get('legal_sections', [])
            
            for section in legal_sections:
                act = section.get('act', '')
                section_num = section.get('section', '')
                
                # Verify section validity
                validity = self.web_researcher.verify_section_validity(act, section_num)
                web_research['section_validity'][f"{act}_{section_num}"] = validity
                
                # Search for amendments
                amendments = self.web_researcher.search_latest_amendments(act)
                web_research['legal_updates'].extend(amendments)
            
            # Get case precedents
            case_type = legal_summary.get('case_type', '')
            if case_type:
                precedents = self.web_researcher.get_case_precedents(
                    case_type.lower().replace(' ', '_')
                )
                web_research['case_precedents'].extend(precedents)
                
                # Get judicial guidelines
                guidelines = self.web_researcher.get_judicial_guidelines(case_type)
                web_research['judicial_guidelines'].extend(guidelines)
            
        except Exception as e:
            web_research['error'] = str(e)
        
        return web_research
    
    def _generate_final_report(self, processed_text: Dict, extracted_info: Dict,
                             legal_mappings: List, legal_summary: Dict,
                             validation_report: Dict, web_research: Dict) -> Dict[str, Any]:
        """Generate comprehensive final report."""
        
        # Convert dataclass objects to dictionaries for JSON serialization
        def convert_dataclass_to_dict(obj):
            if hasattr(obj, '__dict__'):
                return {k: convert_dataclass_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_dataclass_to_dict(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_dataclass_to_dict(v) for k, v in obj.items()}
            else:
                return obj
        
        # Convert extracted info
        converted_extracted_info = convert_dataclass_to_dict(extracted_info)
        
        # Convert legal mappings
        converted_legal_mappings = convert_dataclass_to_dict(legal_mappings)
        
        final_report = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'language_detected': processed_text['language_info']['primary_language'],
                'is_mixed_language': processed_text['language_info']['is_mixed']
            },
            
            'text_processing': {
                'original_text': processed_text['original_text'],
                'language_composition': processed_text['language_info'],
                'telugu_terms_found': processed_text['telugu_terms'],
                'text_segments': processed_text['segments']
            },
            
            'extracted_information': converted_extracted_info,
            
            'legal_analysis': {
                'case_type': legal_summary.get('case_type', ''),
                'legal_sections': legal_summary.get('legal_sections', []),
                'total_sections': legal_summary.get('total_sections', 0),
                'bail_status': legal_summary.get('bail_status', {}),
                'punishment_summary': legal_summary.get('punishment_summary', {}),
                'investigation_priority': legal_summary.get('investigation_priority', 'medium'),
                'special_provisions': legal_summary.get('special_provisions', [])
            },
            
            'legal_mappings': converted_legal_mappings,
            
            'validation_report': validation_report,
            
            'web_research': web_research,
            
            'recommendations': self._generate_recommendations(
                legal_summary, validation_report, web_research
            ),
            
            'export_formats': {
                'json': True,
                'pdf': True,
                'word': True
            }
        }
        
        return final_report
    
    def _generate_recommendations(self, legal_summary: Dict, validation_report: Dict,
                                web_research: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on validation
        if validation_report.get('validation_summary', {}).get('completeness_score', 0) < 80:
            recommendations.append('Review FIR text for missing critical information')
        
        # Based on legal analysis
        case_type = legal_summary.get('case_type', '')
        if 'SC/ST' in case_type or 'Caste' in case_type:
            recommendations.append('Immediate registration of FIR under SC/ST Atrocities Act')
            recommendations.append('Inform District SP within 24 hours')
            recommendations.append('Appoint Special Public Prosecutor')
        
        if legal_summary.get('investigation_priority') == 'highest':
            recommendations.append('Prioritize investigation - high priority case')
        
        # Based on bail status
        bail_status = legal_summary.get('bail_status', {})
        if not bail_status.get('bail_available', True):
            recommendations.append('Non-bailable offences present - immediate arrest required')
        
        # Based on web research
        if web_research.get('legal_updates'):
            recommendations.append('Check for recent legal amendments affecting this case')
        
        if web_research.get('case_precedents'):
            recommendations.append('Review relevant case precedents for investigation guidance')
        
        return recommendations
    
    def analyze_fir_from_sample(self, sample_text: str = None) -> Dict[str, Any]:
        """Analyze the provided sample FIR text."""
        if not sample_text:
            sample_text = """
            On 14th September 2025, at about 8:15 PM, complainant Rajesh Kumar, S/o Venkat Rao, 
            aged 34 years, Scheduled Caste, occupation: Agricultural labourer, resident of Gollapadu 
            village, Bhimavaram Mandal, reported that while he was returning from weekly shandy on 
            his bicycle carrying groceries, he was intercepted near Narsapur Road culvert by a group 
            of four persons.
            
            The accused are identified as:
            Ramesh Babu, aged about 28, S/o Narayana, resident of Gollapadu, known history-sheeter.
            Srinivas, aged about 30, brother-in-law of village sarpanch.
            Murali Krishna, aged about 32, driver, resident of Mogaltur.
            One unknown person, medium build, wearing black shirt.
            
            They came on two motorbikes (Red Pulsar AP-37-BX-4321 and Black Splendor AP-37-CQ-9187) 
            and obstructed him. Ramesh Babu and Srinivas abused him by caste name, shouting 'Mala lanj…' 
            in public view. Murali Krishna pointed a country-made pistol and fired one round in the air, 
            while the unknown person beat him with a stick, causing bleeding injury on his left arm. 
            They forcibly snatched his Samsung mobile phone worth ₹15,000 and ₹12,500 cash from his pocket. 
            They further threatened that if he complained to police, they would kill him and set fire to his hut.
            
            Local villagers (Suresh, Koteswara Rao, and Lakshmi) witnessed the incident but ran away in fear. 
            Rajesh Kumar fell on the ground and was later rescued by passers-by who shifted him to 
            Bhimavaram Government Hospital. ఈ సంఘటన వలన అతను చాలా భయాందోళనకు గురయ్యాడు.
            """
        
        return self.analyze_fir(sample_text, include_web_research=True)
    
    def export_analysis(self, analysis_result: Dict[str, Any], format_type: str = 'json') -> str:
        """Export analysis result in specified format."""
        if format_type == 'json':
            return json.dumps(analysis_result, indent=2, ensure_ascii=False)
        elif format_type == 'summary':
            return self._generate_text_summary(analysis_result)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_text_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Generate human-readable text summary."""
        summary_parts = []
        
        # Basic info
        metadata = analysis_result.get('analysis_metadata', {})
        summary_parts.append(f"FIR Analysis Report - {metadata.get('timestamp', 'N/A')}")
        summary_parts.append("=" * 50)
        
        # Case type
        legal_analysis = analysis_result.get('legal_analysis', {})
        case_type = legal_analysis.get('case_type', 'Unknown')
        summary_parts.append(f"Case Type: {case_type}")
        
        # Legal sections
        legal_sections = legal_analysis.get('legal_sections', [])
        if legal_sections:
            summary_parts.append("\nApplicable Legal Sections:")
            for section in legal_sections:
                summary_parts.append(f"- {section.get('act', '')} Section {section.get('section', '')}: {section.get('title', '')}")
        
        # Recommendations
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            summary_parts.append("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                summary_parts.append(f"{i}. {rec}")
        
        return "\n".join(summary_parts)
