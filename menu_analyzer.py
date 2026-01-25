import google.generativeai as genai
import json
import time
import re
from typing import List
from google.api_core import exceptions

class MenuAnalyzer:
    def __init__(self, api_key: str, base_timeout: float = 2.0, max_retries: int = 3):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
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
                response = self.model.generate_content(prompt)
                text_response = response.text.strip()
                
                # Clean up potential markdown formatting if the model ignores the instruction
                if text_response.startswith("```json"):
                    text_response = text_response[7:]
                if text_response.endswith("```"):
                    text_response = text_response[:-3]
                
                menu_items = json.loads(text_response)
                return menu_items

            except (exceptions.ResourceExhausted, exceptions.TooManyRequests) as e:
                if attempt == self.max_retries:
                    print(f"Error analyzing menu for {restaurant_name}: {e}")
                    return ["Could not extract menu recommendations."]

                # Default backoff
                wait_time = self.base_timeout * (2 ** attempt)
                found_specific_time = False

                # 1. Check structured gRPC details for retry_delay
                if hasattr(e, 'details') and e.details:
                    for detail in e.details:
                        # Check for QuotaFailure or similar objects with 'retry_delay'
                        # The log shows: violations { ... } , retry_delay { seconds: 12 }
                        # We look for any object that has a 'retry_delay' attribute
                        if hasattr(detail, 'retry_delay'):
                            delay_obj = detail.retry_delay
                            # protobuf Duration has 'seconds' and 'nanos'
                            seconds = getattr(delay_obj, 'seconds', 0)
                            nanos = getattr(delay_obj, 'nanos', 0)
                            if seconds > 0 or nanos > 0:
                                wait_time = float(seconds) + (float(nanos) / 1e9) + 0.5
                                found_specific_time = True
                                break

                # 2. Check message for "retry in X s" (Gemini specific)
                if not found_specific_time:
                    # pattern: "Please retry in 12.466568264s"
                    match = re.search(r'retry in (\d+(\.\d+)?)s', str(e))
                    if match:
                        # Add a small buffer to the suggested time
                        wait_time = float(match.group(1)) + 0.5

                print(f"Rate limited for {restaurant_name}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

            except Exception as e:
                print(f"Error analyzing menu for {restaurant_name}: {e}")
                return ["Could not extract menu recommendations."]
        
        return ["Could not extract menu recommendations."]
