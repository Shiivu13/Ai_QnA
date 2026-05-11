import google.generativeai as genai
from app.core.config import settings
import numpy as np

class GeminiService:
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.embed_model = 'models/embedding-001'
        else:
            self.model = None
            print("WARNING: GEMINI_API_KEY not found in settings.")

    def get_embedding(self, text):
        if not self.model:
            return np.zeros((1, 768)) # Dummy fallback
        
        result = genai.embed_content(
            model=self.embed_model,
            content=text,
            task_type="retrieval_document"
        )
        return np.array([result['embedding']])

    async def get_answer(self, query, context):
        if not self.model:
            return "Gemini API not configured. Please provide a GEMINI_API_KEY."

        prompt = f"""
        You are an expert AI assistant specialized in analyzing video content.
        Use the following context from a video transcription to answer the user's question.
        If the answer is not in the context, say that you don't know based on the provided video.

        CONTEXT:
        {context}

        QUESTION:
        {query}

        ANSWER:
        """
        
        response = await self.model.generate_content_async(prompt)
        return response.text

gemini_service = GeminiService()
