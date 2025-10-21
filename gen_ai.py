from google import genai
import re
import json

client = genai.Client(api_key="AIzaSyDxzLjorh4rE013acivV_EioV0P-DEKxxU")

def query_json(query):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=query,
    )

    return response.text


def parse_gemini_json(response_text):
    """
    Cleans and converts a JSON string into a valid Python dictionary.
    Handles escaped characters and ensures proper JSON structure.
    """
    try:
        # Debug print
        print("Raw response:", response_text)
        
        # Step 1: Remove markdown code blocks if present
        cleaned = re.sub(r'```json\s*(.*?)\s*```', r'\1', response_text, flags=re.DOTALL)
        cleaned = re.sub(r'```\s*(.*?)\s*```', r'\1', cleaned, flags=re.DOTALL)
        
        # Step 2: Remove any extra escapes
        cleaned = cleaned.replace('\\"', '"').replace('\\n', '').strip()
        
        # Step 3: Handle double-encoded JSON
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        
        # Debug print
        print("Cleaned JSON:", cleaned)
        
        # Step 4: Parse the JSON string
        try:
            return json.loads(cleaned)
        except:
            # Try parsing with ast.literal_eval as fallback
            import ast
            return ast.literal_eval(cleaned)

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {str(e)}")
        print(f"Failed JSON string: {cleaned}")
        return None
    except Exception as e:
        print(f"[parse_gemini_json] Error: {str(e)}")
        return None


if __name__ == '__main__':
    print(query_json("Explain how AI works in a few words"))