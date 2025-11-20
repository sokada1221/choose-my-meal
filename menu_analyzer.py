import google.generativeai as genai
import json
from typing import List

class MenuAnalyzer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-flash-latest')

    def analyze_reviews(self, restaurant_name: str, reviews: List[str]) -> List[str]:
        """
        Analyzes reviews to extract recommended menu items using Gemini.
        """
        if not reviews:
            return []

        # Combine reviews into a single text block (limit length if necessary)
        reviews_text = "\n".join([f"- {r}" for r in reviews[:10]]) # Limit to top 10 reviews to avoid context limit issues

        prompt = f"""
        You are a food critic assistant. I will provide you with a list of customer reviews for a restaurant named "{restaurant_name}".
        Your task is to identify the top 3 most recommended, signature, or highly praised menu items based on these reviews.
        
        Return ONLY a raw JSON list of strings. Do not include markdown formatting (like ```json).
        Example output: ["Truffle Pizza", "Spicy Tuna Roll", "Tiramisu"]

        Reviews:
        {reviews_text}
        """

        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Clean up potential markdown formatting if the model ignores the instruction
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            menu_items = json.loads(text_response)
            return menu_items
        except Exception as e:
            print(f"Error analyzing menu for {restaurant_name}: {e}")
            return ["Could not extract menu recommendations."]
