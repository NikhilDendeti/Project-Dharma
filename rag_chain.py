import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

load_dotenv()

VECTORSTORE_DIR = "./legal_vectorstore"

def load_documents():
    files = [
        ("kb/1701607577CrimeinIndia2022Book1 (1).pdf", "IPC"),
        ("kb/repealedfileopen.pdf", "CrPC"),
        ("kb/RTI_logo_guidelines_ENGLISH.pdf", "RTI"),
        ("kb/Standard_Operating_Procedures.pdf", "NCRB"),
        ("kb/the_code_of_criminal_procedure,_1973.pdf", "CCP"),
        ("kb/BHARATIYA NAGARIK SURAKSHA SANHITA.pdf", "BNSS")
    ]
    documents = []
    for file, label in files:
        loader = PyMuPDFLoader(file)
        docs = loader.load()
        for doc in docs:
            doc.metadata["document"] = label
            doc.metadata["page"] = doc.metadata.get("page", 0)
        documents.extend(docs)
    return documents

def create_vectorstore(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    return vectorstore

def load_vectorstore():
    retriever = Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=OpenAIEmbeddings()
    ).as_retriever(search_kwargs={"k": 5})
    return retriever

def get_qa_chain():
    # Check if vectorstore exists, else build
    if not os.path.exists(VECTORSTORE_DIR) or not os.listdir(VECTORSTORE_DIR):
        documents = load_documents()
        create_vectorstore(documents)

    retriever = load_vectorstore()

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
You are a legal assistant. Interpret real-life legal scenarios and explain what laws apply based on the documents (IPC, CrPC, RTI, NCRB).
Return the relevant legal section(s) and explain what the person should do (e.g., file FIR, approach RTI, etc).

Use only the context provided. Cite like (IPC, p.23). If not found, say "Not available in the documents."

Context:
{context}

Question: {question}

Answer:
"""
    )

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )
    return chain
