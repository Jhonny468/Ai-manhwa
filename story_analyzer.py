import json
from openai import OpenAI
from app.core.config import settings
from app.schemas.story import StoryAnalysisResult

SYSTEM_PROMPT = """You are a careful literary adaptation analyst preparing a novel for a manhwa production pipeline. Extract only facts supported by the supplied text. Distinguish explicit facts from uncertain details; do not invent character appearances, relationships, locations or events. Keep names consistent. Return concise but useful production notes. The input may be only part of a novel, so mark uncertain fields clearly in descriptions."""

class StoryAnalyzer:
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Add it to backend/.env")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def analyze(self, novel_text: str) -> dict:
        # Phase 1 MVP: limit one analysis request to a manageable excerpt.
        # Phase 2 will chunk long novels and merge chapter-level analyses.
        excerpt = novel_text[:100_000]
        response = self.client.responses.parse(
            model=settings.openai_text_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": "Analyze this novel text for manhwa adaptation:\n\n" + excerpt},
            ],
            text_format=StoryAnalysisResult,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("The AI did not return a structured story analysis.")
        return parsed.model_dump()
