"""
Test Enhanced Prompt for FIR Analysis
====================================

Tests the enhanced OpenAI prompt to ensure it produces the exact format
specified by the user with perfect accuracy.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fir_analyzer.main_analyzer import FIRAnalyzer
import json


def test_enhanced_prompt():
    """Test the enhanced prompt with the sample FIR text."""
    
    # Sample FIR text (the one provided in the task)
    sample_fir_text = """
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
    
    print("🧪 Testing Enhanced OpenAI Prompt for FIR Analysis")
    print("=" * 60)
    
    try:
        # Initialize analyzer
        analyzer = FIRAnalyzer()
        print("✅ FIR Analyzer initialized successfully")
        
        # Test the enhanced extraction method directly
        print("\n📝 Testing enhanced OpenAI extraction...")
        
        # Get processed text first
        processed_text = analyzer.text_processor.process_fir_text(sample_fir_text)
        
        # Test the enhanced extraction
        extracted_info = analyzer._enhanced_extraction_with_openai(
            processed_text['processed_text'], 
            sample_fir_text
        )
        
        print("✅ Enhanced extraction completed successfully!")
        
        # Display the extracted information in the exact format
        print("\n" + "=" * 60)
        print("📊 EXTRACTED INFORMATION (EXACT FORMAT)")
        print("=" * 60)
        
        # Pretty print the JSON
        print(json.dumps(extracted_info, indent=2, ensure_ascii=False))
        
        # Validate the format
        print("\n" + "=" * 60)
        print("✅ FORMAT VALIDATION")
        print("=" * 60)
        
        required_fields = [
            'Complainant', 'DateTime', 'Place', 'Accused', 'Vehicles', 
            'WeaponsUsed', 'Offences', 'Injuries', 'PropertyLoss', 
            'Threats', 'Witnesses', 'Impact'
        ]
        
        validation_results = {}
        for field in required_fields:
            if field in extracted_info:
                validation_results[field] = "✅ Present"
            else:
                validation_results[field] = "❌ Missing"
        
        for field, status in validation_results.items():
            print(f"{field}: {status}")
        
        # Check complainant structure
        complainant = extracted_info.get('Complainant', {})
        complainant_fields = ['Name', 'Father', 'Age', 'Community', 'Occupation', 'Address']
        
        print(f"\nComplainant Structure:")
        for field in complainant_fields:
            if field in complainant:
                print(f"  {field}: ✅ Present - {complainant[field]}")
            else:
                print(f"  {field}: ❌ Missing")
        
        # Check accused structure
        accused = extracted_info.get('Accused', [])
        print(f"\nAccused Structure: {len(accused)} persons found")
        for i, acc in enumerate(accused, 1):
            print(f"  Accused {i}: {acc.get('Name', 'Unknown')}")
            print(f"    Age: {acc.get('Age', 'N/A')}")
            print(f"    Relation: {acc.get('Relation', 'N/A')}")
            print(f"    History: {acc.get('History', 'N/A')}")
        
        # Check expected values
        print(f"\n" + "=" * 60)
        print("🎯 EXPECTED VALUES VALIDATION")
        print("=" * 60)
        
        expected_values = {
            'Complainant.Name': 'Rajesh Kumar',
            'Complainant.Age': 34,
            'Complainant.Community': 'Scheduled Caste',
            'Complainant.Occupation': 'Agricultural labourer',
            'DateTime': '14-09-2025, 8:15 PM',
            'Place': 'Narsapur Road culvert, Bhimavaram',
            'Vehicles': ['AP-37-BX-4321 (Red Pulsar)', 'AP-37-CQ-9187 (Black Splendor)'],
            'WeaponsUsed': ['Country-made pistol', 'Stick'],
            'Offences': ['Caste abuse', 'Threat with firearm', 'Robbery', 'Assault causing injury'],
            'Witnesses': ['Suresh', 'Koteswara Rao', 'Lakshmi']
        }
        
        for key, expected in expected_values.items():
            if '.' in key:
                # Nested field
                parts = key.split('.')
                actual = extracted_info
                for part in parts:
                    actual = actual.get(part, {})
            else:
                actual = extracted_info.get(key, [])
            
            if actual == expected:
                print(f"✅ {key}: Correct - {actual}")
            else:
                print(f"❌ {key}: Expected {expected}, Got {actual}")
        
        # Save results
        with open('enhanced_prompt_test_result.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "=" * 60)
        print("✅ ENHANCED PROMPT TEST COMPLETED!")
        print("📁 Results saved to 'enhanced_prompt_test_result.json'")
        print("=" * 60)
        
        return extracted_info
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_enhanced_prompt()
