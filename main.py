from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rag_chain import get_qa_chain
from deep_translator import GoogleTranslator
from fir_analyzer.main_analyzer import FIRAnalyzer

app = FastAPI()
qa_chain = get_qa_chain()
fir_analyzer = FIRAnalyzer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    language: str = "en"

class FIRAnalysisRequest(BaseModel):
    fir_text: str
    include_web_research: bool = True 

def translate_answer(text: str, target_lang: str) -> str:
    if target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        return f"[Translation error: {e}]\n\n{text}"

@app.post("/chat/text")
async def text_chat(req: QueryRequest):
    print("Received query:", req.query)
    
    try:
        result = qa_chain.invoke({"query": req.query})
        answer_en = result['result']
        answer = translate_answer(answer_en, req.language)

        sources = [
            {
                "page": doc.metadata.get("page", "N/A"),
                "document": doc.metadata.get("document", "N/A"),
                "snippet": doc.page_content[:300]
            }
            for doc in result.get('source_documents', [])
        ]

        return JSONResponse({
            "query": req.query,
            "language": req.language,
            "response": answer,
            "response_en": answer_en,
            "sources": sources
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Something went wrong processing the request."}
        )

@app.post("/fir/analyze")
async def analyze_fir(req: FIRAnalysisRequest):
    """Analyze FIR text and provide legal mapping."""
    print("Received FIR analysis request")
    
    try:
        result = fir_analyzer.analyze_fir(
            req.fir_text, 
            include_web_research=req.include_web_research
        )
        
        if result.get('error'):
            return JSONResponse(
                status_code=500,
                content={"error": result.get('error_message', 'Analysis failed')}
            )
        
        return JSONResponse(result)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "FIR analysis failed."}
        )

@app.post("/fir/analyze/sample")
async def analyze_sample_fir():
    """Analyze the provided sample FIR text."""
    try:
        result = fir_analyzer.analyze_fir_from_sample()
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Sample FIR analysis failed."}
        )
