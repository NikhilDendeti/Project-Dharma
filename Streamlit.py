import streamlit as st
import requests
from dotenv import load_dotenv
import os
import json

# Load .env for any frontend-side values (if needed)
load_dotenv()

st.set_page_config(page_title="📚 Legal Q&A Assistant", layout="centered")

# Sidebar navigation
page = st.sidebar.selectbox("Choose a page", ["Legal Q&A", "FIR Analysis"])

if page == "Legal Q&A":
    st.title("📚 Legal Question Answering")
    st.info("Ask any question based on IPC, CrPC, RTI, NCRB documents.")
elif page == "FIR Analysis":
    st.title("🚨 FIR Analysis System")
    st.info("Analyze First Information Reports with legal section mapping.")

backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8080")

if page == "Legal Q&A":
    language = st.selectbox("Select Language for Answer", ["en", "hi", "te"])
    question = st.text_area("Your Question", placeholder="e.g., What is Section 302 of IPC?")

    if st.button("Submit", key="submit_button") and question.strip():
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{backend_url}/chat/text",
                    json={"query": question, "language": language}
                )

                if response.status_code == 200:
                    res = response.json()
                    st.markdown(f"### 🧠 Answer:\n{res['response']}")

                    # Show RAG sources
                    if res.get("sources"):
                        st.markdown("### 📄 Sources used:")
                        for i, src in enumerate(res["sources"], start=1):
                            st.markdown(
                                f"**{i}. Document:** `{src['document']}` | **Page:** `{src['page']}`\n\n"
                                f"`{src['snippet']}...`\n"
                            )
                else:
                    st.error(f"❌ Error: {response.status_code}\n{response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Connection Error: {e}")

elif page == "FIR Analysis":
    st.markdown("### 📝 Enter FIR Text")
    
    # Sample FIR text
    sample_fir = """On 14th September 2025, at about 8:15 PM, complainant Rajesh Kumar, S/o Venkat Rao, aged 34 years, Scheduled Caste, occupation: Agricultural labourer, resident of Gollapadu village, Bhimavaram Mandal, reported that while he was returning from weekly shandy on his bicycle carrying groceries, he was intercepted near Narsapur Road culvert by a group of four persons.

The accused are identified as:
Ramesh Babu, aged about 28, S/o Narayana, resident of Gollapadu, known history-sheeter.
Srinivas, aged about 30, brother-in-law of village sarpanch.
Murali Krishna, aged about 32, driver, resident of Mogaltur.
One unknown person, medium build, wearing black shirt.

They came on two motorbikes (Red Pulsar AP-37-BX-4321 and Black Splendor AP-37-CQ-9187) and obstructed him. Ramesh Babu and Srinivas abused him by caste name, shouting 'Mala lanj…' in public view. Murali Krishna pointed a country-made pistol and fired one round in the air, while the unknown person beat him with a stick, causing bleeding injury on his left arm. They forcibly snatched his Samsung mobile phone worth ₹15,000 and ₹12,500 cash from his pocket. They further threatened that if he complained to police, they would kill him and set fire to his hut.

Local villagers (Suresh, Koteswara Rao, and Lakshmi) witnessed the incident but ran away in fear. Rajesh Kumar fell on the ground and was later rescued by passers-by who shifted him to Bhimavaram Government Hospital. ఈ సంఘటన వలన అతను చాలా భయాందోళనకు గురయ్యాడు."""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fir_text = st.text_area(
            "FIR Text (English/Telugu/Mixed)", 
            value=sample_fir,
            height=300,
            placeholder="Enter the FIR text here..."
        )
    
    with col2:
        st.markdown("**Options:**")
        include_web_research = st.checkbox("Include Web Research", value=True)
        use_sample = st.button("Use Sample FIR", key="sample_button")
        
        if use_sample:
            st.rerun()
    
    if st.button("Analyze FIR", key="analyze_button") and fir_text.strip():
        with st.spinner("Analyzing FIR..."):
            try:
                response = requests.post(
                    f"{backend_url}/fir/analyze",
                    json={
                        "fir_text": fir_text,
                        "include_web_research": include_web_research
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.success("✅ FIR Analysis Complete!")
                    
                    # Analysis metadata
                    metadata = result.get('analysis_metadata', {})
                    st.markdown(f"**Analysis Time:** {metadata.get('timestamp', 'N/A')}")
                    st.markdown(f"**Language Detected:** {metadata.get('language_detected', 'N/A')}")
                    
                    # Legal Analysis
                    legal_analysis = result.get('legal_analysis', {})
                    st.markdown("### ⚖️ Legal Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Case Type", legal_analysis.get('case_type', 'N/A'))
                    with col2:
                        st.metric("Legal Sections", legal_analysis.get('total_sections', 0))
                    with col3:
                        st.metric("Investigation Priority", legal_analysis.get('investigation_priority', 'N/A'))
                    
                    # Legal Sections
                    legal_sections = legal_analysis.get('legal_sections', [])
                    if legal_sections:
                        st.markdown("#### 📋 Applicable Legal Sections:")
                        for section in legal_sections:
                            with st.expander(f"{section.get('act', '')} Section {section.get('section', '')}: {section.get('title', '')}"):
                                st.write(f"**Description:** {section.get('description', '')}")
                                st.write(f"**Punishment:** {section.get('punishment', '')}")
                                st.write(f"**Bailable:** {'Yes' if section.get('bailable') else 'No'}")
                                st.write(f"**Cognizable:** {'Yes' if section.get('cognizable') else 'No'}")
                    
                    # Extracted Information (Enhanced Format)
                    extracted_info = result.get('extracted_information', {})
                    if extracted_info:
                        st.markdown("### 📊 Extracted Information (Enhanced Format)")
                        
                        # Complainant (Enhanced Format)
                        complainant = extracted_info.get('Complainant', {})
                        if complainant:
                            st.markdown("#### 👤 Complainant Details:")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write(f"**Name:** {complainant.get('Name', 'N/A')}")
                                st.write(f"**Father:** {complainant.get('Father', 'N/A')}")
                            with col2:
                                st.write(f"**Age:** {complainant.get('Age', 'N/A')}")
                                st.write(f"**Community:** {complainant.get('Community', 'N/A')}")
                            with col3:
                                st.write(f"**Occupation:** {complainant.get('Occupation', 'N/A')}")
                                st.write(f"**Address:** {complainant.get('Address', 'N/A')}")
                        
                        # DateTime and Place
                        st.markdown("#### 📅 Incident Details:")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Date & Time:** {extracted_info.get('DateTime', 'N/A')}")
                        with col2:
                            st.write(f"**Place:** {extracted_info.get('Place', 'N/A')}")
                        
                        # Accused (Enhanced Format)
                        accused = extracted_info.get('Accused', [])
                        if accused:
                            st.markdown("#### 🚨 Accused Details:")
                            for i, acc in enumerate(accused, 1):
                                with st.expander(f"Accused {i}: {acc.get('Name', 'Unknown')}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Age:** {acc.get('Age', 'N/A')}")
                                        st.write(f"**Relation:** {acc.get('Relation', 'N/A')}")
                                    with col2:
                                        st.write(f"**History:** {acc.get('History', 'N/A')}")
                                        st.write(f"**Occupation:** {acc.get('Occupation', 'N/A')}")
                                    st.write(f"**Address:** {acc.get('Address', 'N/A')}")
                        
                        # Additional Details
                        st.markdown("#### 🔍 Additional Details:")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Vehicles:** {', '.join(extracted_info.get('Vehicles', []))}")
                            st.write(f"**Weapons Used:** {', '.join(extracted_info.get('WeaponsUsed', []))}")
                            st.write(f"**Offences:** {', '.join(extracted_info.get('Offences', []))}")
                        with col2:
                            st.write(f"**Injuries:** {extracted_info.get('Injuries', 'N/A')}")
                            st.write(f"**Property Loss:** {', '.join(extracted_info.get('PropertyLoss', []))}")
                            st.write(f"**Threats:** {', '.join(extracted_info.get('Threats', []))}")
                        
                        # Witnesses and Impact
                        st.write(f"**Witnesses:** {', '.join(extracted_info.get('Witnesses', []))}")
                        st.write(f"**Impact:** {extracted_info.get('Impact', 'N/A')}")
                    
                    # Validation Report
                    validation_report = result.get('validation_report', {})
                    if validation_report:
                        st.markdown("### ✅ Validation Report")
                        validation_summary = validation_report.get('validation_summary', {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Completeness Score", f"{validation_summary.get('completeness_score', 0)}%")
                        with col2:
                            st.metric("Quality Score", validation_report.get('quality_score', 'N/A'))
                        
                        # Critical Errors
                        critical_errors = validation_report.get('critical_errors', [])
                        if critical_errors:
                            st.error("**Critical Errors:**")
                            for error in critical_errors:
                                st.write(f"• {error}")
                        
                        # Suggestions
                        suggestions = validation_report.get('suggestions', [])
                        if suggestions:
                            st.info("**Suggestions:**")
                            for suggestion in suggestions:
                                st.write(f"• {suggestion}")
                    
                    # Recommendations
                    recommendations = result.get('recommendations', [])
                    if recommendations:
                        st.markdown("### 💡 Recommendations")
                        for i, rec in enumerate(recommendations, 1):
                            st.write(f"{i}. {rec}")
                    
                    # Web Research
                    web_research = result.get('web_research', {})
                    if web_research and include_web_research:
                        st.markdown("### 🌐 Web Research")
                        
                        # Legal Updates
                        legal_updates = web_research.get('legal_updates', [])
                        if legal_updates:
                            st.markdown("#### 📰 Recent Legal Updates:")
                            for update in legal_updates:
                                with st.expander(f"{update.get('act', '')} - {update.get('amendment_date', '')}"):
                                    st.write(f"**Description:** {update.get('description', '')}")
                                    st.write(f"**Impact:** {update.get('impact', '')}")
                        
                        # Case Precedents
                        precedents = web_research.get('case_precedents', [])
                        if precedents:
                            st.markdown("#### ⚖️ Relevant Case Precedents:")
                            for precedent in precedents:
                                with st.expander(f"{precedent.get('case_name', '')} ({precedent.get('year', '')})"):
                                    st.write(f"**Citation:** {precedent.get('citation', '')}")
                                    st.write(f"**Key Principle:** {precedent.get('key_principle', '')}")
                                    st.write(f"**Relevance:** {precedent.get('relevance', '')}")
                
                else:
                    st.error(f"❌ Error: {response.status_code}\n{response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"🚫 Connection Error: {e}")
