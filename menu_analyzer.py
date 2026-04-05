from google import genai
from google.genai import errors as genai_errors
import json
import time
import re
from typing import List

_MODEL_ID = "gemini-3-flash-preview"


class MenuAnalyzer:
    def __init__(self, api_key: str, base_timeout: float = 2.0, max_retries: int = 3):
        self._client = genai.Client(api_key=api_key)
        self.base_timeout = base_timeout
        self.max_retries = max_retries

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

        for attempt in range(self.max_retries + 1):
            try:
                response = self._client.models.generate_content(
                    model=_MODEL_ID,
                    contents=prompt,
                )
                text_response = response.text.strip()
                
                # Clean up potential markdown formatting if the model ignores the instruction
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]
                
                menu_items = json.loads(text_response)
                return menu_items

            except (genai_errors.ClientError, genai_errors.ServerError) as e:
                retriable = e.code in (429, 503)
                if not retriable or attempt == self.max_retries:
                    print(f"Error analyzing menu for {restaurant_name}: {e}")
                    return ["Could not extract menu recommendations."]

                wait_time = self.base_timeout * (2 ** attempt)
                found_specific_time = False

                if e.message:
                    match = re.search(r'retry in (\d+(\.\d+)?)s', e.message)
                    if match:
                        wait_time = float(match.group(1)) + 0.5
                        found_specific_time = True

                if not found_specific_time:
                    match = re.search(r'retry in (\d+(\.\d+)?)s', str(e))
                    if match:
                        wait_time = float(match.group(1)) + 0.5

                print(f"Rate limited for {restaurant_name}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

            except Exception as e:
                print(f"Error analyzing menu for {restaurant_name}: {e}")
                return ["Could not extract menu recommendations."]
        
        return ["Could not extract menu recommendations."]
