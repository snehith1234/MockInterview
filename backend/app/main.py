from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.routes import resume_routes, interview_routes
from app.services.llm_client import set_llm_config

app = FastAPI(title="Mock Interview Agent API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LLMConfigMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        api_key = request.headers.get("x-openai-api-key")
        model = request.headers.get("x-llm-model")
        set_llm_config(api_key, model)
        response = await call_next(request)
        return response


app.add_middleware(LLMConfigMiddleware)

app.include_router(resume_routes.router, prefix="/resume", tags=["Resume"])
app.include_router(interview_routes.router, prefix="/interview", tags=["Interview"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Mock Interview Agent API is running"}
