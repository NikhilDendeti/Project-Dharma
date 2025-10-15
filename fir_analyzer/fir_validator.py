"""
FIR Validator
=============

Validates extracted FIR information for completeness, accuracy,
and legal compliance before generating final output.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class ValidationResult:
    """Represents validation result for a field."""
    field: str
    is_valid: bool
    value: Any
    error_message: Optional[str] = None
    suggestions: List[str] = None


@dataclass
class ValidationSummary:
    """Represents overall validation summary."""
    is_valid: bool
    completeness_score: float
    critical_errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class FIRValidator:
    """Validates extracted FIR information."""
    
    def __init__(self):
        self.required_fields = {
            'complainant': ['name', 'age', 'address'],
            'incident': ['date', 'time', 'place'],
            'offences': ['type', 'description']
        }
        
        self.validation_rules = {
            'name': self._validate_name,
            'age': self._validate_age,
            'date': self._validate_date,
            'time': self._validate_time,
            'amount': self._validate_amount,
            'vehicle_number': self._validate_vehicle_number,
            'phone_number': self._validate_phone_number
        }
    
    def validate_complainant(self, complainant: Any) -> List[ValidationResult]:
        """Validate complainant information."""
        results = []
        
        if not complainant:
            results.append(ValidationResult(
                field='complainant',
                is_valid=False,
                value=None,
                error_message='Complainant information is missing'
            ))
            return results
        
        # Validate name
        if hasattr(complainant, 'name'):
            name_result = self._validate_name(complainant.name)
            results.append(ValidationResult(
                field='complainant.name',
                is_valid=name_result['is_valid'],
                value=complainant.name,
                error_message=name_result.get('error'),
                suggestions=name_result.get('suggestions', [])
            ))
        
        # Validate age
        if hasattr(complainant, 'age'):
            age_result = self._validate_age(complainant.age)
            results.append(ValidationResult(
                field='complainant.age',
                is_valid=age_result['is_valid'],
                value=complainant.age,
                error_message=age_result.get('error'),
                suggestions=age_result.get('suggestions', [])
            ))
        
        # Validate address
        if hasattr(complainant, 'address'):
            address_result = self._validate_address(complainant.address)
            results.append(ValidationResult(
                field='complainant.address',
                is_valid=address_result['is_valid'],
                value=complainant.address,
                error_message=address_result.get('error'),
                suggestions=address_result.get('suggestions', [])
            ))
        
        return results
    
    def validate_accused(self, accused_list: List[Any]) -> List[ValidationResult]:
        """Validate accused information."""
        results = []
        
        if not accused_list:
            results.append(ValidationResult(
                field='accused',
                is_valid=False,
                value=None,
                error_message='No accused persons identified',
                suggestions=['Check if accused details are mentioned in FIR']
            ))
            return results
        
        for i, accused in enumerate(accused_list):
            if not hasattr(accused, 'name') or not accused.name:
                results.append(ValidationResult(
                    field=f'accused[{i}].name',
                    is_valid=False,
                    value=None,
                    error_message='Accused name is missing',
                    suggestions=['Extract accused name from FIR text']
                ))
            else:
                name_result = self._validate_name(accused.name)
                results.append(ValidationResult(
                    field=f'accused[{i}].name',
                    is_valid=name_result['is_valid'],
                    value=accused.name,
                    error_message=name_result.get('error'),
                    suggestions=name_result.get('suggestions', [])
                ))
        
        return results
    
    def validate_incident_details(self, incident: Dict[str, Any]) -> List[ValidationResult]:
        """Validate incident details."""
        results = []
        
        # Validate date
        if 'date' in incident:
            date_result = self._validate_date(incident['date'])
            results.append(ValidationResult(
                field='incident.date',
                is_valid=date_result['is_valid'],
                value=incident['date'],
                error_message=date_result.get('error'),
                suggestions=date_result.get('suggestions', [])
            ))
        else:
            results.append(ValidationResult(
                field='incident.date',
                is_valid=False,
                value=None,
                error_message='Incident date is missing',
                suggestions=['Extract date from FIR text']
            ))
        
        # Validate time
        if 'time' in incident:
            time_result = self._validate_time(incident['time'])
            results.append(ValidationResult(
                field='incident.time',
                is_valid=time_result['is_valid'],
                value=incident['time'],
                error_message=time_result.get('error'),
                suggestions=time_result.get('suggestions', [])
            ))
        
        # Validate place
        if 'place' in incident:
            place_result = self._validate_place(incident['place'])
            results.append(ValidationResult(
                field='incident.place',
                is_valid=place_result['is_valid'],
                value=incident['place'],
                error_message=place_result.get('error'),
                suggestions=place_result.get('suggestions', [])
            ))
        else:
            results.append(ValidationResult(
                field='incident.place',
                is_valid=False,
                value=None,
                error_message='Incident place is missing',
                suggestions=['Extract place from FIR text']
            ))
        
        return results
    
    def validate_offences(self, offences: List[Any]) -> List[ValidationResult]:
        """Validate offence information."""
        results = []
        
        if not offences:
            results.append(ValidationResult(
                field='offences',
                is_valid=False,
                value=None,
                error_message='No offences identified',
                suggestions=['Review FIR text for offence descriptions']
            ))
            return results
        
        for i, offence in enumerate(offences):
            if hasattr(offence, 'type') and offence.type:
                results.append(ValidationResult(
                    field=f'offences[{i}].type',
                    is_valid=True,
                    value=offence.type,
                    suggestions=[]
                ))
            else:
                results.append(ValidationResult(
                    field=f'offences[{i}].type',
                    is_valid=False,
                    value=None,
                    error_message='Offence type is missing',
                    suggestions=['Categorize offence from description']
                ))
        
        return results
    
    def validate_evidence(self, extracted_info: Dict[str, Any]) -> List[ValidationResult]:
        """Validate evidence information."""
        results = []
        
        # Check for witnesses
        witnesses = extracted_info.get('witnesses', [])
        if not witnesses:
            results.append(ValidationResult(
                field='witnesses',
                is_valid=False,
                value=None,
                error_message='No witnesses identified',
                suggestions=['Look for witness names in FIR text']
            ))
        else:
            results.append(ValidationResult(
                field='witnesses',
                is_valid=True,
                value=witnesses,
                suggestions=[]
            ))
        
        # Check for weapons
        weapons = extracted_info.get('weapons', [])
        if weapons:
            for i, weapon in enumerate(weapons):
                if hasattr(weapon, 'type') and weapon.type:
                    results.append(ValidationResult(
                        field=f'weapons[{i}].type',
                        is_valid=True,
                        value=weapon.type,
                        suggestions=[]
                    ))
        
        # Check for vehicles
        vehicles = extracted_info.get('vehicles', [])
        if vehicles:
            for i, vehicle in enumerate(vehicles):
                if hasattr(vehicle, 'number') and vehicle.number:
                    vehicle_result = self._validate_vehicle_number(vehicle.number)
                    results.append(ValidationResult(
                        field=f'vehicles[{i}].number',
                        is_valid=vehicle_result['is_valid'],
                        value=vehicle.number,
                        error_message=vehicle_result.get('error'),
                        suggestions=vehicle_result.get('suggestions', [])
                    ))
        
        return results
    
    def validate_complete_fir(self, extracted_info: Dict[str, Any]) -> ValidationSummary:
        """Validate complete FIR information."""
        all_results = []
        
        # Validate complainant
        complainant = extracted_info.get('complainant')
        all_results.extend(self.validate_complainant(complainant))
        
        # Validate accused
        accused = extracted_info.get('accused', [])
        all_results.extend(self.validate_accused(accused))
        
        # Validate incident
        incident = extracted_info.get('incident', {})
        all_results.extend(self.validate_incident_details(incident))
        
        # Validate offences
        offences = extracted_info.get('offences', [])
        all_results.extend(self.validate_offences(offences))
        
        # Validate evidence
        all_results.extend(self.validate_evidence(extracted_info))
        
        # Calculate summary
        total_fields = len(all_results)
        valid_fields = sum(1 for result in all_results if result.is_valid)
        completeness_score = (valid_fields / total_fields * 100) if total_fields > 0 else 0
        
        critical_errors = [result.error_message for result in all_results 
                          if not result.is_valid and result.error_message]
        
        warnings = []
        suggestions = []
        
        for result in all_results:
            if result.suggestions:
                suggestions.extend(result.suggestions)
        
        return ValidationSummary(
            is_valid=len(critical_errors) == 0,
            completeness_score=completeness_score,
            critical_errors=critical_errors,
            warnings=warnings,
            suggestions=list(set(suggestions))  # Remove duplicates
        )
    
    def _validate_name(self, name: str) -> Dict[str, Any]:
        """Validate name format."""
        if not name or not name.strip():
            return {
                'is_valid': False,
                'error': 'Name is empty',
                'suggestions': ['Extract name from FIR text']
            }
        
        if len(name.strip()) < 2:
            return {
                'is_valid': False,
                'error': 'Name too short',
                'suggestions': ['Check if full name is extracted']
            }
        
        if not re.match(r'^[A-Za-z\s\.]+$', name.strip()):
            return {
                'is_valid': False,
                'error': 'Name contains invalid characters',
                'suggestions': ['Clean name format']
            }
        
        return {'is_valid': True}
    
    def _validate_age(self, age: int) -> Dict[str, Any]:
        """Validate age."""
        if not age:
            return {
                'is_valid': False,
                'error': 'Age is missing',
                'suggestions': ['Extract age from FIR text']
            }
        
        if not isinstance(age, int):
            return {
                'is_valid': False,
                'error': 'Age must be a number',
                'suggestions': ['Convert age to integer']
            }
        
        if age < 0 or age > 120:
            return {
                'is_valid': False,
                'error': 'Age out of reasonable range',
                'suggestions': ['Verify age extraction']
            }
        
        return {'is_valid': True}
    
    def _validate_date(self, date: str) -> Dict[str, Any]:
        """Validate date format."""
        if not date:
            return {
                'is_valid': False,
                'error': 'Date is missing',
                'suggestions': ['Extract date from FIR text']
            }
        
        # Check various date formats
        date_patterns = [
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}\s+\w+\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, date):
                return {'is_valid': True}
        
        return {
            'is_valid': False,
            'error': 'Invalid date format',
            'suggestions': ['Use DD-MM-YYYY or DD/MM/YYYY format']
        }
    
    def _validate_time(self, time: str) -> Dict[str, Any]:
        """Validate time format."""
        if not time:
            return {'is_valid': True}  # Time is optional
        
        time_pattern = r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)'
        if re.search(time_pattern, time):
            return {'is_valid': True}
        
        return {
            'is_valid': False,
            'error': 'Invalid time format',
            'suggestions': ['Use HH:MM AM/PM format']
        }
    
    def _validate_amount(self, amount: str) -> Dict[str, Any]:
        """Validate amount format."""
        if not amount:
            return {'is_valid': True}  # Amount is optional
        
        amount_pattern = r'₹\s*[\d,]+(?:\.\d{2})?'
        if re.search(amount_pattern, amount):
            return {'is_valid': True}
        
        return {
            'is_valid': False,
            'error': 'Invalid amount format',
            'suggestions': ['Use ₹ symbol with number']
        }
    
    def _validate_vehicle_number(self, vehicle_number: str) -> Dict[str, Any]:
        """Validate vehicle number format."""
        if not vehicle_number:
            return {'is_valid': True}  # Vehicle number is optional
        
        vehicle_pattern = r'[A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4}'
        if re.search(vehicle_pattern, vehicle_number):
            return {'is_valid': True}
        
        return {
            'is_valid': False,
            'error': 'Invalid vehicle number format',
            'suggestions': ['Use format: XX-XX-XX-XXXX']
        }
    
    def _validate_phone_number(self, phone: str) -> Dict[str, Any]:
        """Validate phone number format."""
        if not phone:
            return {'is_valid': True}  # Phone number is optional
        
        phone_pattern = r'\b\d{10}\b'
        if re.search(phone_pattern, phone):
            return {'is_valid': True}
        
        return {
            'is_valid': False,
            'error': 'Invalid phone number format',
            'suggestions': ['Use 10-digit number']
        }
    
    def _validate_address(self, address: str) -> Dict[str, Any]:
        """Validate address format."""
        if not address or not address.strip():
            return {
                'is_valid': False,
                'error': 'Address is missing',
                'suggestions': ['Extract address from FIR text']
            }
        
        if len(address.strip()) < 5:
            return {
                'is_valid': False,
                'error': 'Address too short',
                'suggestions': ['Check if complete address is extracted']
            }
        
        return {'is_valid': True}
    
    def _validate_place(self, place: str) -> Dict[str, Any]:
        """Validate place format."""
        if not place or not place.strip():
            return {
                'is_valid': False,
                'error': 'Place is missing',
                'suggestions': ['Extract place from FIR text']
            }
        
        return {'is_valid': True}
    
    def generate_validation_report(self, extracted_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        validation_summary = self.validate_complete_fir(extracted_info)
        
        report = {
            'validation_summary': {
                'is_valid': validation_summary.is_valid,
                'completeness_score': round(validation_summary.completeness_score, 2),
                'critical_errors_count': len(validation_summary.critical_errors),
                'suggestions_count': len(validation_summary.suggestions)
            },
            'critical_errors': validation_summary.critical_errors,
            'suggestions': validation_summary.suggestions,
            'recommendations': self._generate_recommendations(validation_summary),
            'quality_score': self._calculate_quality_score(validation_summary)
        }
        
        return report
    
    def _generate_recommendations(self, validation_summary: ValidationSummary) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if validation_summary.completeness_score < 70:
            recommendations.append('Review FIR text for missing information')
        
        if validation_summary.critical_errors:
            recommendations.append('Address critical errors before proceeding')
        
        if 'complainant' in str(validation_summary.critical_errors):
            recommendations.append('Ensure complainant details are complete')
        
        if 'accused' in str(validation_summary.critical_errors):
            recommendations.append('Verify accused person details')
        
        if 'incident' in str(validation_summary.critical_errors):
            recommendations.append('Complete incident details')
        
        return recommendations
    
    def _calculate_quality_score(self, validation_summary: ValidationSummary) -> str:
        """Calculate overall quality score."""
        score = validation_summary.completeness_score
        
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 60:
            return 'Poor'
        else:
            return 'Very Poor'
