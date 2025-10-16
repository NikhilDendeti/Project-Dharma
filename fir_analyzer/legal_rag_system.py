"""
Legal RAG System for FIR Analysis
=================================

Provides Retrieval-Augmented Generation capabilities for FIR analysis
using the local ChromaDB knowledge base with web search fallback.
"""

import os
from typing import Dict, List, Optional, Any
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
import json
from datetime import datetime


class LegalRAGSystem:
    """RAG system for legal research with local KB priority and web search fallback."""
    
    def __init__(self):
        self.vectorstore_dir = "./legal_vectorstore"
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize or load the ChromaDB vector store."""
        try:
            if os.path.exists(self.vectorstore_dir) and os.listdir(self.vectorstore_dir):
                # Load existing vectorstore
                self.vectorstore = Chroma(
                    persist_directory=self.vectorstore_dir,
                    embedding_function=self.embeddings
                )
                print("✓ Loaded existing ChromaDB vector store")
            else:
                # Create new vectorstore
                self._create_vectorstore()
                print("✓ Created new ChromaDB vector store")
        except Exception as e:
            print(f"Error initializing vectorstore: {e}")
            self.vectorstore = None
    
    def _create_vectorstore(self):
        """Create vectorstore from legal documents."""
        documents = self._load_legal_documents()
        
        if documents:
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Create vectorstore
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.vectorstore_dir
            )
            print(f"✓ Created vectorstore with {len(chunks)} chunks")
    
    def _load_legal_documents(self) -> List[Document]:
        """Load legal documents from the knowledge base."""
        documents = []
        
        # Legal document files
        legal_files = [
            ("kb/1701607577CrimeinIndia2022Book1 (1).pdf", "NCRB_Statistics"),
            ("kb/BHARATIYA NAGARIK SURAKSHA SANHITA.pdf", "BNS_2023"),
            ("kb/the_code_of_criminal_procedure,_1973.pdf", "CrPC_1973"),
            ("kb/Standard_Operating_Procedures.pdf", "NCRB_SOP"),
            ("kb/RTI_logo_guidelines_ENGLISH.pdf", "RTI_Guidelines"),
            ("kb/repealedfileopen.pdf", "Repealed_Acts")
        ]
        
        for file_path, doc_type in legal_files:
            try:
                if os.path.exists(file_path):
                    loader = PyMuPDFLoader(file_path)
                    docs = loader.load()
                    
                    # Add metadata
                    for doc in docs:
                        doc.metadata["document_type"] = doc_type
                        doc.metadata["source_file"] = file_path
                        doc.metadata["page"] = doc.metadata.get("page", 0)
                    
                    documents.extend(docs)
                    print(f"✓ Loaded {len(docs)} pages from {doc_type}")
                else:
                    print(f"⚠ File not found: {file_path}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def search_legal_context(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search for legal context in the local knowledge base."""
        if not self.vectorstore:
            return {
                'found': False,
                'results': [],
                'message': 'Vector store not available'
            }
        
        try:
            # Search for relevant documents
            docs = self.vectorstore.similarity_search(query, k=max_results)
            
            if docs:
                # Process and format results
                results = []
                for doc in docs:
                    result = {
                        'content': doc.page_content,
                        'source': doc.metadata.get('document_type', 'Unknown'),
                        'page': doc.metadata.get('page', 0),
                        'file': doc.metadata.get('source_file', 'Unknown'),
                        'relevance_score': self._calculate_relevance_score(query, doc.page_content)
                    }
                    results.append(result)
                
                # Sort by relevance
                results.sort(key=lambda x: x['relevance_score'], reverse=True)
                
                return {
                    'found': True,
                    'results': results,
                    'total_found': len(results),
                    'query': query,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'found': False,
                    'results': [],
                    'message': 'No relevant documents found in local knowledge base'
                }
        
        except Exception as e:
            return {
                'found': False,
                'results': [],
                'error': str(e),
                'message': 'Error searching local knowledge base'
            }
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """Calculate relevance score between query and content."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        # Simple word overlap scoring
        overlap = len(query_words.intersection(content_words))
        total_query_words = len(query_words)
        
        if total_query_words == 0:
            return 0.0
        
        return overlap / total_query_words
    
    def get_legal_section_context(self, act: str, section: str) -> Dict[str, Any]:
        """Get detailed context for a specific legal section."""
        query = f"{act} section {section} punishment bailable cognizable"
        
        search_result = self.search_legal_context(query, max_results=3)
        
        if search_result['found']:
            # Extract specific information about the section
            section_info = self._extract_section_info(search_result['results'], act, section)
            return {
                'found': True,
                'section_info': section_info,
                'source_documents': search_result['results'],
                'query': query
            }
        else:
            return {
                'found': False,
                'message': f'No information found for {act} Section {section}',
                'query': query
            }
    
    def _extract_section_info(self, results: List[Dict], act: str, section: str) -> Dict[str, Any]:
        """Extract specific section information from search results."""
        section_info = {
            'act': act,
            'section': section,
            'title': '',
            'description': '',
            'punishment': '',
            'bailable': None,
            'cognizable': None,
            'severity': 'medium'
        }
        
        # Combine content from all results
        combined_content = ' '.join([result['content'] for result in results])
        
        # Use LLM to extract structured information
        prompt = f"""
        Extract legal section information from the following text for {act} Section {section}:
        
        Text: {combined_content}
        
        IMPORTANT: Return ONLY a valid JSON object with the following structure. No markdown, no explanations, no additional text.
        
        {{
            "title": "Section title",
            "description": "Section description", 
            "punishment": "Punishment details",
            "bailable": true,
            "cognizable": true,
            "severity": "medium"
        }}
        
        If information is not found, use "Not specified" for text fields and null for boolean fields.
        Return ONLY the JSON object.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()
            
            # Clean the response to extract JSON
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            elif response_content.startswith('```'):
                response_content = response_content[3:]
            
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Try to find JSON object boundaries
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_content = response_content[start_idx:end_idx + 1]
            
            if response_content and response_content.strip():
                extracted_info = json.loads(response_content)
                section_info.update(extracted_info)
            else:
                print(f"Empty response for section info extraction")
                # Use default values
                section_info.update({
                    "title": "Not specified",
                    "description": "Not specified", 
                    "punishment": "Not specified",
                    "bailable": None,
                    "cognizable": None,
                    "severity": "medium"
                })
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in section info: {e}")
            print(f"Raw response: {response_content}")
        except Exception as e:
            print(f"Error extracting section info: {e}")
        
        return section_info
    
    def get_case_precedents(self, offence_type: str, legal_sections: List[str]) -> Dict[str, Any]:
        """Get relevant case precedents from local knowledge base."""
        query = f"{offence_type} case precedents judgments court decisions"
        
        search_result = self.search_legal_context(query, max_results=5)
        
        if search_result['found']:
            precedents = self._extract_precedents(search_result['results'], offence_type)
            return {
                'found': True,
                'precedents': precedents,
                'source_documents': search_result['results']
            }
        else:
            return {
                'found': False,
                'precedents': [],
                'message': f'No precedents found for {offence_type}'
            }
    
    def _extract_precedents(self, results: List[Dict], offence_type: str) -> List[Dict[str, Any]]:
        """Extract case precedents from search results."""
        precedents = []
        
        # Combine content from all results
        combined_content = ' '.join([result['content'] for result in results])
        
        prompt = f"""
        Extract case precedents and judgments from the following text related to {offence_type}:
        
        Text: {combined_content}
        
        IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanations, no additional text.
        
        [
            {{
                "case_name": "Case name",
                "citation": "Court citation",
                "year": "Year",
                "key_principle": "Key legal principle",
                "relevance": "High"
            }}
        ]
        
        If no precedents are found, return an empty array: []
        Return ONLY the JSON array.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()
            
            # Clean the response to extract JSON
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            elif response_content.startswith('```'):
                response_content = response_content[3:]
            
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Try to find JSON array boundaries
            start_idx = response_content.find('[')
            end_idx = response_content.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_content = response_content[start_idx:end_idx + 1]
            
            if response_content:
                precedents = json.loads(response_content)
            else:
                print(f"Empty response for precedents extraction")
                precedents = []
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in precedents: {e}")
            print(f"Raw response: {response_content}")
            precedents = []
        except Exception as e:
            print(f"Error extracting precedents: {e}")
            precedents = []
        
        return precedents
    
    def get_investigation_guidelines(self, case_type: str, legal_sections: List[str]) -> Dict[str, Any]:
        """Get investigation guidelines from local knowledge base."""
        query = f"{case_type} investigation guidelines procedures SOP"
        
        search_result = self.search_legal_context(query, max_results=3)
        
        if search_result['found']:
            guidelines = self._extract_guidelines(search_result['results'], case_type)
            return {
                'found': True,
                'guidelines': guidelines,
                'source_documents': search_result['results']
            }
        else:
            return {
                'found': False,
                'guidelines': [],
                'message': f'No guidelines found for {case_type}'
            }
    
    def _extract_guidelines(self, results: List[Dict], case_type: str) -> List[Dict[str, Any]]:
        """Extract investigation guidelines from search results."""
        guidelines = []
        
        # Combine content from all results
        combined_content = ' '.join([result['content'] for result in results])
        
        prompt = f"""
        Extract investigation guidelines and procedures from the following text for {case_type}:
        
        Text: {combined_content}
        
        IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanations, no additional text.
        
        [
            {{
                "guideline": "Guideline description",
                "source": "Source document",
                "importance": "Critical",
                "time_limit": "Time limit if specified"
            }}
        ]
        
        If no guidelines are found, return an empty array: []
        Return ONLY the JSON array.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()
            
            # Clean the response to extract JSON
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            elif response_content.startswith('```'):
                response_content = response_content[3:]
            
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Try to find JSON array boundaries
            start_idx = response_content.find('[')
            end_idx = response_content.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_content = response_content[start_idx:end_idx + 1]
            
            if response_content:
                guidelines = json.loads(response_content)
            else:
                print(f"Empty response for guidelines extraction")
                guidelines = []
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in guidelines: {e}")
            print(f"Raw response: {response_content}")
            guidelines = []
        except Exception as e:
            print(f"Error extracting guidelines: {e}")
            guidelines = []
        
        return guidelines
    
    def get_legal_updates(self, act: str, section: str = None) -> Dict[str, Any]:
        """Get legal updates and amendments from local knowledge base."""
        if section:
            query = f"{act} section {section} amendments updates 2023 2024 2025"
        else:
            query = f"{act} amendments updates 2023 2024 2025"
        
        search_result = self.search_legal_context(query, max_results=3)
        
        if search_result['found']:
            updates = self._extract_updates(search_result['results'], act, section)
            return {
                'found': True,
                'updates': updates,
                'source_documents': search_result['results']
            }
        else:
            return {
                'found': False,
                'updates': [],
                'message': f'No updates found for {act}'
            }
    
    def _extract_updates(self, results: List[Dict], act: str, section: str = None) -> List[Dict[str, Any]]:
        """Extract legal updates from search results."""
        updates = []
        
        # Combine content from all results
        combined_content = ' '.join([result['content'] for result in results])
        
        prompt = f"""
        Extract legal updates and amendments from the following text for {act}:
        
        Text: {combined_content}
        
        IMPORTANT: Return ONLY a valid JSON array. No markdown, no explanations, no additional text.
        
        [
            {{
                "update_type": "Amendment",
                "date": "Date of update",
                "description": "Description of update",
                "impact": "Impact on legal practice",
                "source": "Source document"
            }}
        ]
        
        If no updates are found, return an empty array: []
        Return ONLY the JSON array.
        """
        
        try:
            response = self.llm.invoke(prompt)
            response_content = response.content.strip()
            
            # Clean the response to extract JSON
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            elif response_content.startswith('```'):
                response_content = response_content[3:]
            
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            response_content = response_content.strip()
            
            # Try to find JSON array boundaries
            start_idx = response_content.find('[')
            end_idx = response_content.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                response_content = response_content[start_idx:end_idx + 1]
            
            if response_content:
                updates = json.loads(response_content)
            else:
                print(f"Empty response for updates extraction")
                updates = []
                
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in updates: {e}")
            print(f"Raw response: {response_content}")
            updates = []
        except Exception as e:
            print(f"Error extracting updates: {e}")
            updates = []
        
        return updates
    
    def get_comprehensive_legal_research(self, legal_sections: List[Dict], case_type: str) -> Dict[str, Any]:
        """Get comprehensive legal research combining multiple sources."""
        research_results = {
            'legal_sections': [],
            'precedents': [],
            'guidelines': [],
            'updates': [],
            'local_kb_used': True,
            'web_search_required': False
        }
        
        # Research each legal section
        for section in legal_sections:
            act = section.get('act', '')
            section_num = section.get('section', '')
            
            # Get section context
            section_context = self.get_legal_section_context(act, section_num)
            if section_context['found']:
                research_results['legal_sections'].append(section_context)
            
            # Get legal updates
            updates = self.get_legal_updates(act, section_num)
            if updates['found']:
                research_results['updates'].extend(updates['updates'])
        
        # Get case precedents
        precedents = self.get_case_precedents(case_type, [s.get('section', '') for s in legal_sections])
        if precedents['found']:
            research_results['precedents'] = precedents['precedents']
        
        # Get investigation guidelines
        guidelines = self.get_investigation_guidelines(case_type, [s.get('section', '') for s in legal_sections])
        if guidelines['found']:
            research_results['guidelines'] = guidelines['guidelines']
        
        # Determine if web search is needed
        total_results = (len(research_results['legal_sections']) + 
                        len(research_results['precedents']) + 
                        len(research_results['guidelines']) + 
                        len(research_results['updates']))
        
        if total_results < 2:  # Need at least 2 results from local KB
            research_results['web_search_required'] = True
            research_results['local_kb_used'] = False
            print(f"⚠️ Local KB insufficient (only {total_results} results), web search required")
        else:
            research_results['web_search_required'] = False
            research_results['local_kb_used'] = True
            print(f"✅ Local KB sufficient ({total_results} results found)")
        
        return research_results
