"""
Legal Section Mapper
===================

Maps extracted FIR information to relevant legal sections from
BNS 2023, SC/ST Atrocities Act, Arms Act, and other relevant laws.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class LegalSection:
    """Represents a legal section with details."""
    act: str
    section: str
    title: str
    description: str
    punishment: str
    bailable: bool
    cognizable: bool
    severity: str


@dataclass
class LegalMapping:
    """Represents the legal mapping for an offence."""
    offence_type: str
    sections: List[LegalSection]
    investigation_steps: List[str]
    evidence_required: List[str]
    time_limits: Dict[str, str]


class LegalSectionMapper:
    """Maps FIR information to relevant legal sections."""
    
    def __init__(self):
        self.legal_sections = self._initialize_legal_sections()
        self.offence_mappings = self._initialize_offence_mappings()
    
    def _initialize_legal_sections(self) -> Dict[str, Dict[str, LegalSection]]:
        """Initialize the legal sections database."""
        sections = {
            'BNS_2023': {
                '309': LegalSection(
                    act='BNS 2023',
                    section='309',
                    title='Robbery',
                    description='Theft with use of force or threat of force',
                    punishment='Imprisonment for 3-10 years and fine',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                ),
                '115': LegalSection(
                    act='BNS 2023',
                    section='115',
                    title='Hurt',
                    description='Causing bodily pain, disease or infirmity',
                    punishment='Imprisonment up to 1 year or fine up to ₹10,000',
                    bailable=True,
                    cognizable=True,
                    severity='medium'
                ),
                '351': LegalSection(
                    act='BNS 2023',
                    section='351',
                    title='Criminal Intimidation',
                    description='Threatening to cause injury to person, property or reputation',
                    punishment='Imprisonment up to 2 years or fine or both',
                    bailable=True,
                    cognizable=True,
                    severity='medium'
                ),
                '113': LegalSection(
                    act='BNS 2023',
                    section='113',
                    title='Grievous Hurt',
                    description='Causing grievous hurt with dangerous weapon',
                    punishment='Imprisonment for 3-7 years and fine',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                ),
                '120': LegalSection(
                    act='BNS 2023',
                    section='120',
                    title='Unlawful Assembly',
                    description='Assembly of 5 or more persons with common object',
                    punishment='Imprisonment up to 6 months or fine or both',
                    bailable=True,
                    cognizable=True,
                    severity='medium'
                )
            },
            'SC_ST_Atrocities_Act_1989': {
                '3_1_r': LegalSection(
                    act='SC/ST Atrocities Act, 1989',
                    section='3(1)(r)',
                    title='Intentional Insult/Abuse by Caste Name',
                    description='Intentionally insults or intimidates with intent to humiliate on grounds of caste',
                    punishment='Imprisonment for 6 months to 5 years and fine',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                ),
                '3_2_v': LegalSection(
                    act='SC/ST Atrocities Act, 1989',
                    section='3(2)(v)',
                    title='Offence Committed on Ground of Caste',
                    description='Commits any offence under IPC/BNS on grounds of caste',
                    punishment='Same as IPC/BNS but with enhanced punishment',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                )
            },
            'Arms_Act_1959': {
                '25': LegalSection(
                    act='Arms Act, 1959',
                    section='25',
                    title='Possession of Illegal Arms',
                    description='Possession of arms without license',
                    punishment='Imprisonment for 1-3 years and fine',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                ),
                '27': LegalSection(
                    act='Arms Act, 1959',
                    section='27',
                    title='Use of Firearm in Commission of Offence',
                    description='Using firearm in commission of any offence',
                    punishment='Imprisonment for 3-7 years and fine',
                    bailable=False,
                    cognizable=True,
                    severity='high'
                )
            },
            'Motor_Vehicles_Act_1988': {
                '66': LegalSection(
                    act='Motor Vehicles Act, 1988',
                    section='66',
                    title='Unauthorized Use of Vehicle',
                    description='Using vehicle for unlawful purpose',
                    punishment='Fine up to ₹5,000 or imprisonment up to 3 months',
                    bailable=True,
                    cognizable=False,
                    severity='low'
                )
            }
        }
        return sections
    
    def _initialize_offence_mappings(self) -> Dict[str, List[str]]:
        """Initialize offence to legal section mappings."""
        return {
            'caste_atrocity': ['SC_ST_Atrocities_Act_1989.3_1_r', 'SC_ST_Atrocities_Act_1989.3_2_v'],
            'robbery': ['BNS_2023.309'],
            'assault': ['BNS_2023.115', 'BNS_2023.113'],
            'criminal_intimidation': ['BNS_2023.351'],
            'arms_offence': ['Arms_Act_1959.25', 'Arms_Act_1959.27'],
            'rioting': ['BNS_2023.120'],
            'vehicle_offence': ['Motor_Vehicles_Act_1988.66']
        }
    
    def map_offences_to_sections(self, offences: List[Any]) -> List[LegalMapping]:
        """Map extracted offences to legal sections."""
        mappings = []
        
        for offence in offences:
            # Handle both string offences and object offences
            if isinstance(offence, str):
                offence_type = self._categorize_offence(offence)
            else:
                offence_type = offence.type if hasattr(offence, 'type') else str(offence)
            
            if offence_type in self.offence_mappings:
                section_refs = self.offence_mappings[offence_type]
                legal_sections = []
                
                for ref in section_refs:
                    act, section = ref.split('.')
                    if act in self.legal_sections and section in self.legal_sections[act]:
                        legal_sections.append(self.legal_sections[act][section])
                
                if legal_sections:
                    mapping = LegalMapping(
                        offence_type=offence_type,
                        sections=legal_sections,
                        investigation_steps=self._get_investigation_steps(offence_type),
                        evidence_required=self._get_evidence_required(offence_type),
                        time_limits=self._get_time_limits(offence_type)
                    )
                    mappings.append(mapping)
        
        return mappings
    
    def _categorize_offence(self, offence_description: str) -> str:
        """Categorize offence description to offence type."""
        offence_lower = offence_description.lower()
        
        if any(keyword in offence_lower for keyword in ['caste', 'sc', 'st', 'scheduled']):
            return 'caste_atrocity'
        elif any(keyword in offence_lower for keyword in ['rob', 'robbery', 'snatch', 'theft']):
            return 'robbery'
        elif any(keyword in offence_lower for keyword in ['assault', 'hurt', 'beat', 'attack']):
            return 'assault'
        elif any(keyword in offence_lower for keyword in ['threat', 'intimidation']):
            return 'criminal_intimidation'
        elif any(keyword in offence_lower for keyword in ['pistol', 'gun', 'weapon', 'firearm']):
            return 'arms_offence'
        elif any(keyword in offence_lower for keyword in ['vehicle', 'motorbike', 'bike']):
            return 'vehicle_offence'
        else:
            return 'general_offence'
    
    def _get_investigation_steps(self, offence_type: str) -> List[str]:
        """Get investigation steps for specific offence type."""
        steps = {
            'caste_atrocity': [
                'Register FIR immediately',
                'Inform District SP within 24 hours',
                'Conduct spot inspection',
                'Record statements of witnesses',
                'Collect medical evidence',
                'Arrest accused persons',
                'File charge sheet within 60 days'
            ],
            'robbery': [
                'Register FIR immediately',
                'Conduct spot inspection',
                'Record statements of witnesses',
                'Collect CCTV footage if available',
                'Arrest accused persons',
                'Recover stolen property',
                'File charge sheet within 90 days'
            ],
            'assault': [
                'Register FIR immediately',
                'Get medical examination done',
                'Record statements of witnesses',
                'Arrest accused persons',
                'File charge sheet within 90 days'
            ],
            'arms_offence': [
                'Register FIR immediately',
                'Recover weapon used',
                'Get ballistic examination',
                'Arrest accused persons',
                'File charge sheet within 90 days'
            ]
        }
        return steps.get(offence_type, ['Register FIR', 'Investigate', 'File charge sheet'])
    
    def _get_evidence_required(self, offence_type: str) -> List[str]:
        """Get evidence required for specific offence type."""
        evidence = {
            'caste_atrocity': [
                'Medical certificate',
                'Witness statements',
                'Caste certificate of complainant',
                'Spot inspection report',
                'Photographs of scene'
            ],
            'robbery': [
                'Medical certificate',
                'Witness statements',
                'Recovery memo of stolen property',
                'CCTV footage',
                'Vehicle details'
            ],
            'assault': [
                'Medical certificate',
                'Witness statements',
                'Weapon used (if any)',
                'Photographs of injuries'
            ],
            'arms_offence': [
                'Weapon recovered',
                'Ballistic report',
                'Witness statements',
                'Arms license verification'
            ]
        }
        return evidence.get(offence_type, ['Medical certificate', 'Witness statements'])
    
    def _get_time_limits(self, offence_type: str) -> Dict[str, str]:
        """Get time limits for specific offence type."""
        limits = {
            'caste_atrocity': {
                'FIR_registration': 'Immediately',
                'SP_notification': 'Within 24 hours',
                'Charge_sheet': 'Within 60 days',
                'Trial_completion': 'Within 2 years'
            },
            'robbery': {
                'FIR_registration': 'Immediately',
                'Charge_sheet': 'Within 90 days',
                'Trial_completion': 'Within 2 years'
            },
            'assault': {
                'FIR_registration': 'Immediately',
                'Charge_sheet': 'Within 90 days',
                'Trial_completion': 'Within 1 year'
            }
        }
        return limits.get(offence_type, {
            'FIR_registration': 'Immediately',
            'Charge_sheet': 'Within 90 days'
        })
    
    def get_enhanced_punishment(self, base_section: LegalSection, is_caste_atrocity: bool = False) -> str:
        """Get enhanced punishment for caste atrocity cases."""
        if is_caste_atrocity and base_section.act in ['BNS 2023', 'IPC']:
            return f"{base_section.punishment} (Enhanced under SC/ST Act)"
        return base_section.punishment
    
    def suggest_bail_conditions(self, sections: List[LegalSection]) -> Dict[str, Any]:
        """Suggest bail conditions based on legal sections."""
        bailable_sections = [s for s in sections if s.bailable]
        non_bailable_sections = [s for s in sections if not s.bailable]
        
        if non_bailable_sections:
            return {
                'bail_available': False,
                'reason': 'Non-bailable offences present',
                'sections': [s.section for s in non_bailable_sections]
            }
        else:
            return {
                'bail_available': True,
                'conditions': [
                    'Personal bond of ₹50,000',
                    'Two sureties of ₹25,000 each',
                    'Not to tamper with evidence',
                    'Not to contact witnesses',
                    'Regular appearance in court'
                ]
            }
    
    def calculate_total_punishment(self, sections: List[LegalSection]) -> Dict[str, Any]:
        """Calculate total punishment range."""
        max_imprisonment = 0
        total_fine = 0
        severity_levels = []
        
        for section in sections:
            # Extract imprisonment years (simplified)
            imprisonment_match = re.search(r'(\d+)-?(\d+)?\s*years?', section.punishment)
            if imprisonment_match:
                min_years = int(imprisonment_match.group(1))
                max_years = int(imprisonment_match.group(2)) if imprisonment_match.group(2) else min_years
                max_imprisonment = max(max_imprisonment, max_years)
            
            # Extract fine amount (simplified)
            fine_match = re.search(r'₹\s*([\d,]+)', section.punishment)
            if fine_match:
                fine_amount = int(fine_match.group(1).replace(',', ''))
                total_fine += fine_amount
            
            severity_levels.append(section.severity)
        
        return {
            'max_imprisonment_years': max_imprisonment,
            'total_fine': f"₹{total_fine:,}" if total_fine > 0 else "As per court discretion",
            'overall_severity': 'high' if 'high' in severity_levels else 'medium' if 'medium' in severity_levels else 'low',
            'concurrent_sentences': 'Sentences may run concurrently as per court discretion'
        }
    
    def generate_legal_summary(self, extracted_info: Dict[str, Any], legal_mappings: List[LegalMapping]) -> Dict[str, Any]:
        """Generate comprehensive legal summary."""
        summary = {
            'case_type': self._determine_case_type(extracted_info),
            'legal_sections': [],
            'total_sections': 0,
            'bail_status': {},
            'punishment_summary': {},
            'investigation_priority': 'high',
            'special_provisions': []
        }
        
        all_sections = []
        for mapping in legal_mappings:
            all_sections.extend(mapping.sections)
        
        summary['legal_sections'] = [
            {
                'act': section.act,
                'section': section.section,
                'title': section.title,
                'description': section.description,
                'punishment': section.punishment,
                'bailable': section.bailable,
                'cognizable': section.cognizable
            }
            for section in all_sections
        ]
        
        summary['total_sections'] = len(all_sections)
        summary['bail_status'] = self.suggest_bail_conditions(all_sections)
        summary['punishment_summary'] = self.calculate_total_punishment(all_sections)
        
        # Check for special provisions
        if any('SC/ST' in section.act for section in all_sections):
            summary['special_provisions'].append('SC/ST Atrocities Act provisions apply')
            summary['investigation_priority'] = 'highest'
        
        if any('Arms' in section.act for section in all_sections):
            summary['special_provisions'].append('Arms Act provisions apply')
        
        return summary
    
    def _determine_case_type(self, extracted_info: Dict[str, Any]) -> str:
        """Determine the type of case based on extracted information."""
        # Check complainant community
        complainant = extracted_info.get('Complainant', {})
        if complainant:
            community = complainant.get('Community', '')
            if community and ('SC' in community or 'ST' in community or 'Scheduled' in community):
                return 'SC/ST Atrocity Case'
        
        # Check offences
        offences = extracted_info.get('Offences', [])
        if offences:
            offence_text = ' '.join(offences).lower()
            if any(keyword in offence_text for keyword in ['caste', 'sc', 'st', 'scheduled']):
                return 'SC/ST Atrocity Case'
            elif any(keyword in offence_text for keyword in ['rob', 'robbery', 'snatch']):
                return 'Robbery Case'
            elif any(keyword in offence_text for keyword in ['pistol', 'gun', 'weapon', 'firearm']):
                return 'Arms Offence Case'
            elif any(keyword in offence_text for keyword in ['assault', 'hurt', 'beat']):
                return 'Assault Case'
        
        return 'General Criminal Case'
