import google.generativeai as genai
import os
from typing import Optional

class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

    async def summarize_pr(self, title: str, body: str, diff_summary: str = "") -> str:
        prompt = f"""
        You are an expert software engineer. Please summarize the following Pull Request.
        
        Title: {title}
        
        Description:
        {body}
        
        {diff_summary}
        
        Provide a concise summary of the changes, the intent, and any potential risks. 
        Format your response in Markdown.
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
