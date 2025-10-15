"""
Test Script for FIR Analyzer
============================

Demonstrates the FIR analysis system with the provided sample text.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fir_analyzer.main_analyzer import FIRAnalyzer
import json


def test_fir_analyzer():
    """Test the FIR analyzer with sample text."""
    
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
    
    print("🚨 FIR Analysis System Test")
    print("=" * 50)
    
    try:
        # Initialize analyzer
        analyzer = FIRAnalyzer()
        print("✅ FIR Analyzer initialized successfully")
        
        # Analyze the FIR
        print("\n📝 Analyzing FIR text...")
        result = analyzer.analyze_fir(sample_fir_text, include_web_research=True)
        
        if result.get('error'):
            print(f"❌ Analysis failed: {result.get('error_message')}")
            return
        
        print("✅ FIR Analysis completed successfully!")
        
        # Display results
        print("\n" + "=" * 50)
        print("📊 ENHANCED FIR ANALYSIS RESULTS")
        print("=" * 50)
        
        # Analysis metadata
        metadata = result.get('analysis_metadata', {})
        print(f"📅 Analysis Time: {metadata.get('timestamp', 'N/A')}")
        print(f"🌐 Language Detected: {metadata.get('language_detected', 'N/A')}")
        print(f"🔄 Mixed Language: {metadata.get('is_mixed_language', False)}")
        
        # Legal Analysis
        legal_analysis = result.get('legal_analysis', {})
        print(f"\n⚖️  CASE TYPE: {legal_analysis.get('case_type', 'N/A')}")
        print(f"📋 Total Legal Sections: {legal_analysis.get('total_sections', 0)}")
        print(f"🚨 Investigation Priority: {legal_analysis.get('investigation_priority', 'N/A')}")
        
        # Legal Sections
        legal_sections = legal_analysis.get('legal_sections', [])
        if legal_sections:
            print(f"\n📋 APPLICABLE LEGAL SECTIONS:")
            for section in legal_sections:
                print(f"  • {section.get('act', '')} Section {section.get('section', '')}: {section.get('title', '')}")
                print(f"    Description: {section.get('description', '')}")
                print(f"    Punishment: {section.get('punishment', '')}")
                print(f"    Bailable: {'Yes' if section.get('bailable') else 'No'}")
                print()
        
        # Extracted Information in Exact Format
        extracted_info = result.get('extracted_information', {})
        if extracted_info:
            print("📊 EXTRACTED INFORMATION (EXACT FORMAT):")
            print("=" * 40)
            
            # Display in the exact format requested
            print(f"Complainant:")
            complainant = extracted_info.get('Complainant', {})
            print(f"  Name: {complainant.get('Name', 'N/A')}")
            print(f"  Father: {complainant.get('Father', 'N/A')}")
            print(f"  Age: {complainant.get('Age', 'N/A')}")
            print(f"  Community: {complainant.get('Community', 'N/A')}")
            print(f"  Occupation: {complainant.get('Occupation', 'N/A')}")
            print(f"  Address: {complainant.get('Address', 'N/A')}")
            
            print(f"\nDateTime: {extracted_info.get('DateTime', 'N/A')}")
            print(f"Place: {extracted_info.get('Place', 'N/A')}")
            
            # Accused
            accused = extracted_info.get('Accused', [])
            if accused:
                print(f"\nAccused ({len(accused)} persons):")
                for i, acc in enumerate(accused, 1):
                    print(f"  {i}. {acc.get('Name', 'Unknown')}")
                    print(f"     Age: {acc.get('Age', 'N/A')}")
                    print(f"     Relation: {acc.get('Relation', 'N/A')}")
                    print(f"     History: {acc.get('History', 'N/A')}")
                    print(f"     Occupation: {acc.get('Occupation', 'N/A')}")
                    print(f"     Address: {acc.get('Address', 'N/A')}")
            
            # Vehicles
            vehicles = extracted_info.get('Vehicles', [])
            if vehicles:
                print(f"\nVehicles: {', '.join(vehicles)}")
            
            # Weapons
            weapons = extracted_info.get('WeaponsUsed', [])
            if weapons:
                print(f"Weapons Used: {', '.join(weapons)}")
            
            # Offences
            offences = extracted_info.get('Offences', [])
            if offences:
                print(f"Offences: {', '.join(offences)}")
            
            # Injuries
            injuries = extracted_info.get('Injuries', 'N/A')
            print(f"Injuries: {injuries}")
            
            # Property Loss
            property_loss = extracted_info.get('PropertyLoss', [])
            if property_loss:
                print(f"Property Loss: {', '.join(property_loss)}")
            
            # Threats
            threats = extracted_info.get('Threats', [])
            if threats:
                print(f"Threats: {', '.join(threats)}")
            
            # Witnesses
            witnesses = extracted_info.get('Witnesses', [])
            if witnesses:
                print(f"Witnesses: {', '.join(witnesses)}")
            
            # Impact
            impact = extracted_info.get('Impact', 'N/A')
            print(f"Impact: {impact}")
        
        # Validation Report
        validation_report = result.get('validation_report', {})
        if validation_report:
            print(f"\n✅ VALIDATION REPORT:")
            validation_summary = validation_report.get('validation_summary', {})
            print(f"  Completeness Score: {validation_summary.get('completeness_score', 0)}%")
            print(f"  Quality Score: {validation_report.get('quality_score', 'N/A')}")
            
            critical_errors = validation_report.get('critical_errors', [])
            if critical_errors:
                print(f"  Critical Errors: {len(critical_errors)}")
                for error in critical_errors:
                    print(f"    • {error}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        # Web Research
        web_research = result.get('web_research', {})
        if web_research:
            print(f"\n🌐 WEB RESEARCH (OpenAI + CrewAI):")
            
            legal_updates = web_research.get('legal_updates', [])
            if legal_updates:
                print(f"  Legal Updates: {len(legal_updates)}")
                for update in legal_updates:
                    print(f"    • {update.get('act', '')} - {update.get('amendment_date', '')}")
            
            precedents = web_research.get('case_precedents', [])
            if precedents:
                print(f"  Case Precedents: {len(precedents)}")
                for precedent in precedents:
                    print(f"    • {precedent.get('case_name', '')} ({precedent.get('year', '')})")
        
        print("\n" + "=" * 50)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Save results to file
        with open('fir_analysis_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("📁 Results saved to 'fir_analysis_result.json'")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_fir_analyzer()
