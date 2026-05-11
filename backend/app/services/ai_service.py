import os
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in environment variables.")

async def generate_summary(text: str) -> str:
    """
    Generates a concise and well-structured summary of the provided text 
    using the gemini-3.1-flash-lite model.
    """
    if not text.strip():
        return "No text available to summarize."
        
    try:
        # Load the configuration from api key
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # We use flash as it is the fastest and most cost-effective for summarization
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        prompt = (
            "Please provide a concise and well-structured summary of the following text. "
            "Use bullet points for key takeaways if applicable.\n\n"
            f"TEXT CONTENT:\n{text}"
        )
        
        # Generate content asynchronously
        response = await model.generate_content_async(prompt)
        
        return response.text
        
    except Exception as e:
        return f"An error occurred while generating the summary: {str(e)}"

async def answer_question_with_context(query: str, context: str) -> str:
    """
    Answers a user query based strictly on the provided context 
    using the gemini-3.1-flash-lite model.
    """
    if not query.strip():
        return "Please provide a question."
        
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Construct strict instructions to answer ONLY from the context
        model = genai.GenerativeModel('gemini-3.1-flash-lite')
        
        system_instruction = (
            "You are a helpful AI assistant. Answer the user's question STRICTLY based on the provided context. "
            "If the answer is not contained within the context, politely state that the information is not available "
            "in the processed document. Do not use external knowledge.\n"
            "IMPORTANT: If the context includes Timestamp segments (e.g., [Timestamp: 12.5s - 15.0s]), "
            "you MUST cite the source of your information by including the timestamp directly in your answer "
            "in the exact format [start_s - end_s] (e.g. [12.5s - 15.0s])."
        )
        
        full_prompt = (
            f"{system_instruction}\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"QUESTION:\n{query}\n\n"
            "ANSWER:"
        )
        
        response = await model.generate_content_async(full_prompt)
        
        return response.text
        
    except Exception as e:
        return f"An error occurred while generating the answer: {str(e)}"
