"""
FIR Information Extractor
=========================

Extracts structured information from processed FIR text including
complainant details, accused information, incident details, and offences.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Person:
    """Represents a person in the FIR."""
    name: str
    father_name: Optional[str] = None
    age: Optional[int] = None
    community: Optional[str] = None
    occupation: Optional[str] = None
    address: Optional[str] = None
    relation: Optional[str] = None
    history: Optional[str] = None


@dataclass
class Vehicle:
    """Represents a vehicle mentioned in the FIR."""
    number: str
    type: Optional[str] = None
    color: Optional[str] = None


@dataclass
class Weapon:
    """Represents a weapon used in the incident."""
    type: str
    description: Optional[str] = None


@dataclass
class Offence:
    """Represents an offence committed."""
    type: str
    description: str
    severity: str = "medium"


class FIRInformationExtractor:
    """Extracts structured information from FIR text."""
    
    def __init__(self):
        # Patterns for extracting information
        self.patterns = {
            'date': r'\b(\d{1,2})(?:st|nd|rd|th)?\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
            'time': r'\b(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)\b',
            'age': r'\b(?:aged|age)\s*(\d{1,2})\s*(?:years?)?\b',
            'amount': r'₹\s*([\d,]+(?:\.\d{2})?)',
            'vehicle_number': r'([A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4})',
            'phone_number': r'\b(\d{10})\b',
            'caste_abuse': r'(?:caste|community).*?(?:abuse|insult|slur)',
            'threat': r'(?:threat|threaten).*?(?:kill|harm|damage)',
            'weapon': r'(?:pistol|gun|knife|stick|weapon|firearm)',
            'injury': r'(?:injury|hurt|wound|bleeding|cut)',
            'robbery': r'(?:rob|snatch|steal|theft|dacoity)',
            'assault': r'(?:assault|beat|hit|attack|strike)'
        }
        
        # Community/caste patterns
        self.community_patterns = [
            r'Scheduled Caste',
            r'Scheduled Tribe', 
            r'SC',
            r'ST',
            r'Backward Class',
            r'BC',
            r'General',
            r'OBC'
        ]
        
        # Offence categories
        self.offence_categories = {
            'caste_atrocity': ['caste abuse', 'caste insult', 'caste slur'],
            'robbery': ['robbery', 'dacoity', 'theft', 'snatching'],
            'assault': ['assault', 'hurt', 'grievous hurt', 'simple hurt'],
            'criminal_intimidation': ['threat', 'intimidation', 'criminal intimidation'],
            'arms_offence': ['illegal arms', 'firearm', 'weapon'],
            'rioting': ['rioting', 'unlawful assembly'],
            'kidnapping': ['kidnapping', 'abduction'],
            'sexual_offence': ['rape', 'sexual assault', 'molestation']
        }
    
    def extract_complainant_info(self, text: str) -> Person:
        """Extract complainant information from FIR text."""
        complainant = Person(name="")
        
        # Extract name patterns
        name_patterns = [
            r'complainant\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'informant\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'reported\s+by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*S/o'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                complainant.name = match.group(1)
                break
        
        # Extract father's name
        father_patterns = [
            r'S/o\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'son\s+of\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'father\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in father_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                complainant.father_name = match.group(1)
                break
        
        # Extract age
        age_match = re.search(self.patterns['age'], text, re.IGNORECASE)
        if age_match:
            complainant.age = int(age_match.group(1))
        
        # Extract community
        for pattern in self.community_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                complainant.community = pattern
                break
        
        # Extract occupation
        occupation_patterns = [
            r'occupation:\s*([^,]+)',
            r'profession:\s*([^,]+)',
            r'working\s+as\s+([^,]+)',
            r'([A-Z][a-z]+\s+labourer)',
            r'([A-Z][a-z]+\s+worker)'
        ]
        
        for pattern in occupation_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                complainant.occupation = match.group(1).strip()
                break
        
        # Extract address
        address_patterns = [
            r'resident\s+of\s+([^,]+(?:village|mandal|district|state)[^,]*)',
            r'address:\s*([^,]+)',
            r'living\s+in\s+([^,]+)'
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                complainant.address = match.group(1).strip()
                break
        
        return complainant
    
    def extract_accused_info(self, text: str) -> List[Person]:
        """Extract information about accused persons."""
        accused_list = []
        
        # Split text into accused sections
        accused_sections = re.split(r'(?:accused|suspect|perpetrator)', text, flags=re.IGNORECASE)
        
        for section in accused_sections[1:]:  # Skip first section (before first accused)
            accused = Person(name="")
            
            # Extract name
            name_patterns = [
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'([A-Z][a-z]+),\s*aged'
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, section)
                if match:
                    accused.name = match.group(1)
                    break
            
            # Extract age
            age_match = re.search(r'aged\s+about?\s*(\d{1,2})', section, re.IGNORECASE)
            if age_match:
                accused.age = int(age_match.group(1))
            
            # Extract father's name
            father_match = re.search(r'S/o\s+([A-Z][a-z]+)', section, re.IGNORECASE)
            if father_match:
                accused.father_name = father_match.group(1)
            
            # Extract relation
            relation_patterns = [
                r'brother-in-law\s+of\s+([^,]+)',
                r'relative\s+of\s+([^,]+)',
                r'known\s+([^,]+)'
            ]
            
            for pattern in relation_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    accused.relation = match.group(1).strip()
                    break
            
            # Extract occupation
            occupation_match = re.search(r'([A-Z][a-z]+),\s*resident', section)
            if occupation_match:
                accused.occupation = occupation_match.group(1)
            
            # Extract address
            address_match = re.search(r'resident\s+of\s+([^,]+)', section, re.IGNORECASE)
            if address_match:
                accused.address = address_match.group(1).strip()
            
            # Extract history
            if 'history-sheeter' in section.lower():
                accused.history = 'History-sheeter'
            
            if accused.name:  # Only add if we found a name
                accused_list.append(accused)
        
        return accused_list
    
    def extract_incident_details(self, text: str) -> Dict[str, Any]:
        """Extract incident details from FIR text."""
        details = {
            'date': None,
            'time': None,
            'place': None,
            'sequence': []
        }
        
        # Extract date
        date_match = re.search(self.patterns['date'], text, re.IGNORECASE)
        if date_match:
            day, month, year = date_match.groups()
            details['date'] = f"{day}-{month}-{year}"
        
        # Extract time
        time_match = re.search(self.patterns['time'], text, re.IGNORECASE)
        if time_match:
            hour, minute, period = time_match.groups()
            details['time'] = f"{hour}:{minute} {period.upper()}"
        
        # Extract place
        place_patterns = [
            r'near\s+([^,]+(?:road|culvert|bridge|junction)[^,]*)',
            r'at\s+([^,]+(?:village|mandal|district)[^,]*)',
            r'place:\s*([^,]+)',
            r'location:\s*([^,]+)'
        ]
        
        for pattern in place_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['place'] = match.group(1).strip()
                break
        
        return details
    
    def extract_vehicles(self, text: str) -> List[Vehicle]:
        """Extract vehicle information from FIR text."""
        vehicles = []
        
        # Extract vehicle numbers and descriptions
        vehicle_pattern = r'([A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4})\s*\(([^)]+)\)'
        matches = re.findall(vehicle_pattern, text)
        
        for number, description in matches:
            vehicle = Vehicle(number=number)
            
            # Extract color and type from description
            if 'red' in description.lower():
                vehicle.color = 'Red'
            elif 'black' in description.lower():
                vehicle.color = 'Black'
            elif 'white' in description.lower():
                vehicle.color = 'White'
            
            if 'pulsar' in description.lower():
                vehicle.type = 'Pulsar'
            elif 'splendor' in description.lower():
                vehicle.type = 'Splendor'
            elif 'bike' in description.lower() or 'motorbike' in description.lower():
                vehicle.type = 'Motorbike'
            
            vehicles.append(vehicle)
        
        return vehicles
    
    def extract_weapons(self, text: str) -> List[Weapon]:
        """Extract weapon information from FIR text."""
        weapons = []
        
        weapon_patterns = [
            r'(country-made pistol)',
            r'(pistol)',
            r'(gun)',
            r'(knife)',
            r'(stick)',
            r'(rod)',
            r'(weapon)'
        ]
        
        for pattern in weapon_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                weapon = Weapon(type=match.lower())
                weapons.append(weapon)
        
        return weapons
    
    def extract_offences(self, text: str) -> List[Offence]:
        """Extract offences from FIR text."""
        offences = []
        
        for category, keywords in self.offence_categories.items():
            for keyword in keywords:
                if re.search(keyword, text, re.IGNORECASE):
                    offence = Offence(
                        type=category,
                        description=keyword.title(),
                        severity=self._determine_severity(category)
                    )
                    offences.append(offence)
                    break  # Avoid duplicates
        
        return offences
    
    def extract_witnesses(self, text: str) -> List[str]:
        """Extract witness names from FIR text."""
        witnesses = []
        
        witness_patterns = [
            r'witnessed\s+by\s+([^,]+)',
            r'witnesses?\s+([^,]+)',
            r'seen\s+by\s+([^,]+)',
            r'observed\s+by\s+([^,]+)'
        ]
        
        for pattern in witness_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                witness_text = match.group(1)
                # Split multiple witnesses
                witness_names = [name.strip() for name in witness_text.split(',')]
                witnesses.extend(witness_names)
        
        return witnesses
    
    def extract_property_loss(self, text: str) -> List[Dict[str, Any]]:
        """Extract property loss information."""
        losses = []
        
        # Extract mobile phone
        phone_pattern = r'(Samsung|iPhone|mobile phone).*?₹\s*([\d,]+)'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            losses.append({
                'item': phone_match.group(1) + ' mobile phone',
                'value': f"₹{phone_match.group(2)}"
            })
        
        # Extract cash
        cash_pattern = r'₹\s*([\d,]+)\s*cash'
        cash_match = re.search(cash_pattern, text, re.IGNORECASE)
        if cash_match:
            losses.append({
                'item': 'Cash',
                'value': f"₹{cash_match.group(1)}"
            })
        
        return losses
    
    def extract_injuries(self, text: str) -> List[str]:
        """Extract injury information."""
        injuries = []
        
        injury_patterns = [
            r'(bleeding injury)',
            r'(cut)',
            r'(wound)',
            r'(hurt)',
            r'(injury)'
        ]
        
        for pattern in injury_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            injuries.extend(matches)
        
        return injuries
    
    def _determine_severity(self, offence_type: str) -> str:
        """Determine the severity of an offence."""
        high_severity = ['caste_atrocity', 'sexual_offence', 'kidnapping']
        medium_severity = ['robbery', 'assault', 'arms_offence']
        
        if offence_type in high_severity:
            return 'high'
        elif offence_type in medium_severity:
            return 'medium'
        else:
            return 'low'
    
    def extract_all_information(self, text: str) -> Dict[str, Any]:
        """Extract all information from FIR text in the exact specified format."""
        # Extract individual components
        complainant = self.extract_complainant_info(text)
        accused = self.extract_accused_info(text)
        incident = self.extract_incident_details(text)
        vehicles = self.extract_vehicles(text)
        weapons = self.extract_weapons(text)
        offences = self.extract_offences(text)
        witnesses = self.extract_witnesses(text)
        property_loss = self.extract_property_loss(text)
        injuries = self.extract_injuries(text)
        
        # Format in the exact structure requested
        formatted_info = {
            "Complainant": {
                "Name": complainant.name if hasattr(complainant, 'name') else "N/A",
                "Father": complainant.father_name if hasattr(complainant, 'father_name') else "N/A",
                "Age": complainant.age if hasattr(complainant, 'age') else "N/A",
                "Community": complainant.community if hasattr(complainant, 'community') else "N/A",
                "Occupation": complainant.occupation if hasattr(complainant, 'occupation') else "N/A",
                "Address": complainant.address if hasattr(complainant, 'address') else "N/A"
            },
            "DateTime": f"{incident.get('date', 'N/A')}, {incident.get('time', 'N/A')}",
            "Place": incident.get('place', 'N/A'),
            "Accused": [
                {
                    "Name": acc.name if hasattr(acc, 'name') else "Unknown",
                    "Age": acc.age if hasattr(acc, 'age') else "N/A",
                    "Relation": acc.relation if hasattr(acc, 'relation') else "N/A",
                    "History": acc.history if hasattr(acc, 'history') else "N/A",
                    "Occupation": acc.occupation if hasattr(acc, 'occupation') else "N/A",
                    "Address": acc.address if hasattr(acc, 'address') else "N/A"
                }
                for acc in accused
            ],
            "Vehicles": [f"{v.number} ({v.color} {v.type})" for v in vehicles] if vehicles else [],
            "WeaponsUsed": [w.type for w in weapons] if weapons else [],
            "Offences": [offence.description if hasattr(offence, 'description') else str(offence) for offence in offences] if offences else [],
            "Injuries": ", ".join(injuries) if injuries else "N/A",
            "PropertyLoss": [f"{loss.get('item', 'N/A')} worth {loss.get('value', 'N/A')}" for loss in property_loss] if property_loss else [],
            "Threats": self._extract_threats(text),
            "Witnesses": witnesses if witnesses else [],
            "Impact": self._extract_impact(text)
        }
        
        return formatted_info
    
    def _extract_threats(self, text: str) -> List[str]:
        """Extract threats mentioned in the text."""
        threats = []
        
        # Look for threat patterns
        threat_patterns = [
            r'(?:threat|threaten).*?(?:kill|harm|damage|fire)',
            r'(?:will|would).*?(?:kill|harm|damage)',
            r'(?:set fire|burn)',
            r'(?:destroy|damage).*?(?:house|hut|property)'
        ]
        
        for pattern in threat_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            threats.extend(matches)
        
        return threats
    
    def _extract_impact(self, text: str) -> str:
        """Extract impact/effect of the incident."""
        impact_keywords = [
            'fear', 'afraid', 'scared', 'terrified', 'hospitalized', 'injured',
            'bleeding', 'hurt', 'damage', 'loss', 'trauma', 'shock'
        ]
        
        impacts = []
        for keyword in impact_keywords:
            if keyword in text.lower():
                impacts.append(keyword)
        
        if impacts:
            return f"Incident caused: {', '.join(impacts)}"
        else:
            return "Impact not clearly specified"
