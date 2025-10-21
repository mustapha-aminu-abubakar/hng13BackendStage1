from flask import Flask, jsonify, request, abort
import hashlib
import json
from datetime import datetime, timezone
from gen_ai import query_json, parse_gemini_json
app = Flask(__name__)

with open('strings.json', 'w') as f:
        json.dump({}, f, indent=4)

def is_palindrome(s: str) -> bool:
    """
    Check if a string is a palindrome (reads the same forwards and backwards).
    
    Args:
        s (str): The input string to check
        
    Returns:
        bool: True if the string is a palindrome, False otherwise
    """
    reverse = ''
    for i in range(len(s)-1, -1, -1):
        reverse += s[i]
    return s.lower() == reverse.lower()

def unique_xters(s: str) -> int:
    """
    Count the number of unique characters in a string.
    
    Args:
        s (str): The input string to analyze
        
    Returns:
        int: The count of unique characters in the string
    """
    return len(''.join(set(s)))

def word_count(s: str) -> int:
    """
    Count the number of words in a string.
    
    Args:
        s (str): The input string to analyze
        
    Returns:
        int: The number of words in the string
    """
    words = s.split()
    return len(words)

def count_xters(s: str) -> dict:
    """
    Create a frequency map of characters in a string.
    
    Args:
        s (str): The input string to analyze
        
    Returns:
        dict: A dictionary with characters as keys and their frequencies as values
    """
    d = {}
    for c in s:
        d[c] = d.get(c, 0) + 1
    return d

@app.route('/strings', methods=['POST'])
def add_string():
    """
    Add a new string to the collection.
    
    Expects a JSON payload with a 'value' key containing the string to add.
    Analyzes the string and stores various properties including:
    - Length
    - Palindrome check
    - Unique character count
    - Word count
    - SHA256 hash
    - Character frequency map
    
    Returns:
        tuple: (JSON response, HTTP status code)
        - 201: Successfully created
        - 400: Missing or invalid request body
        - 409: String already exists
        - 422: Invalid value type
    """
    data = request.get_json()
    
    if not data or 'value' not in data:
        return jsonify({'error': 'Bad Request', 'message': 'Missing "value" in JSON body'}), 400
    
    input_string = data['value']
    if not isinstance(input_string, str):
        return jsonify({'error': 'Unprocessable Entity', 'message': '"value" must be a string'}), 422

    input_string_hash = hashlib.sha256(input_string.encode()).hexdigest()
    
    with open('strings.json', 'r') as f:
        json_data = json.load(f)
    if input_string in json_data: return jsonify({'error': 'Conflict', 'message': 'String already exists'}), 409
    
    entry = {
        'value': input_string,
        'id': input_string_hash,
        'properties': {
            'length': len(input_string),
            'is_palindrome': is_palindrome(input_string),
            'unique_characters': unique_xters(input_string),
            'word_count': word_count(input_string),
            'sha256_hash': input_string_hash,
            'character_frequency_map': count_xters(input_string),
        },
        'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    json_data[entry['value']] = entry
    
    with open('strings.json', 'w') as f:
        json.dump(json_data, f, indent=4)
    
    return jsonify(entry), 201 

@app.route('/strings/<string_value>', methods=['GET'])
def get_string(string_value):
    """
    Retrieve a specific string and its properties by value.
    
    Args:
        string_value (str): The string value to look up
        
    Returns:
        tuple: (JSON response, HTTP status code)
        - 200: Success, returns string data
        - 404: String not found
    """
    with open('strings.json', 'r') as f:
        json_data = json.load(f)
    if string_value not in json_data:
        return jsonify({'error': 'Not Found', 'message': 'String not found'}), 404
    return jsonify(json_data[string_value]), 200

@app.route('/strings', methods=['GET'])
def filter_strings():
    """
    Filter strings based on various criteria specified in query parameters.
    
    Query Parameters:
        is_palindrome (str): Filter by palindrome status ('true'/'false')
        min_length (int): Minimum string length
        max_length (int): Maximum string length
        word_count (int): Exact word count to match
        contains_character (str): Character that must be present
        
    Returns:
        tuple: (JSON response, HTTP status code)
        - 200: Success, returns filtered results
        - 400: No strings match the criteria
    """
    is_palindrome = request.args.get('is_palindrome')
    min_length = request.args.get('min_length', type=int)
    max_length = request.args.get('max_length', type=int)
    word_count = request.args.get('word_count', type=int)
    contains_character = request.args.get('contains_character')

    with open('strings.json', 'r') as f:
        json_data = json.load(f)

    results = []
    for entry in json_data.values():
        props = entry['properties']
        # Filter by is_palindrome
        if is_palindrome is not None:
            if str(props['is_palindrome']).lower() != is_palindrome.lower():
                continue
        # Filter by min_length
        if min_length is not None and props['length'] < min_length:
            continue
        # Filter by max_length
        if max_length is not None and props['length'] > max_length:
            continue
        # Filter by word_count
        if word_count is not None and props['word_count'] != word_count:
            continue
        # Filter by contains_character
        if contains_character and contains_character not in entry['value']:
            continue
        results.append(entry)
    
    if len(results) == 0:
        return jsonify({'error': 'Bad Request', 'message': 'No strings found matching the criteria'}), 400
    
    return jsonify(results), 200

@app.route('/strings/filter-by-natural-language', methods=['GET'])
def filter_by_nl():
    """
    Filter strings using natural language queries processed by AI.
    
    Uses Google's Generative AI to interpret natural language queries and filter strings
    based on the interpreted criteria. The AI analyzes the query and returns matching strings
    along with the parsed filters it identified.
    
    Query Parameters:
        query (str): Natural language description of desired filters
        
    Returns:
        tuple: (JSON response, HTTP status code)
        - 200: Success, returns filtered results and interpretation
        - 400: Error in processing query
    """
    filter_string = request.query_string.decode('utf-8')  # Decode to string
    
    with open('strings.json', 'r') as f:
        json_data = json.load(f)

    prompt = f"""
    You are a JSON data filtering engine.

    Below is a JSON dataset and a filter condition.
    Your task is to return ONLY the objects that match the filter condition FROM the JSON data.
    Always include a "parsed_filters" object summarizing all constraints or filters mentioned in the user input (e.g., word_count, is_palindrome, length, etc.).
    Do not add explanations, comments, or any extra text. 
    Output must be a valid JSON object or array that can be parsed directly with `json.loads()`.

    ### Filter condition:
    {filter_string}

    ### JSON data:
    {json_data}

    Return:
    Respond only with valid JSON format without escape characters. Do not include explanations, code blocks, or backticks. Your response must be a single valid JSON object containing only the filtered results

    """
    try:
        response = query_json(prompt)
        response_clean = parse_gemini_json(response['Cleaned JSON'])
        # print('--------------filter', filter_string)
    except Exception as e:
        return jsonify({'error' : str(e)}), 400
    
    # print(response_clean)
    
    output = {
        'interpreted_query': {
        'parsed_filters': response_clean.get('parsed_filters', {}),
        'original': filter_string[6:].replace('%20', ' '),
        },
        'count': len(response_clean.get('filtered_results', [])),
        'data': [obj['value'] for obj in response_clean.get('filtered_results', [])]
    }
    return jsonify(output), 200


@app.route('/strings/<string_value>', methods=['DELETE'])
def delete_entry(string_value):
    """
    Delete a specific string from the collection.
    
    Args:
        string_value (str): The string value to delete
        
    Returns:
        tuple: (Response, HTTP status code)
        - 204: Successfully deleted
        - 404: String not found
    """
    with open('strings.json', 'r') as f:
        json_data = json.load(f)
    if string_value not in json_data:
        return jsonify({'error': 'Not Found', 'message': 'String not found'}), 404
    
    json_data.pop(string_value)
    
    with open('strings.json', 'w') as f:
        json.dump(json_data, f, indent=4)
    return '', 204  # Returns empty response with 204 No Content status code
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
