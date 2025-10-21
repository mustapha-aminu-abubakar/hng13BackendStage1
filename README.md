# String Management API

A Flask-based REST API for string manipulation and analysis. The API provides endpoints for storing, retrieving, and analyzing strings with various properties including palindrome checking, character frequency analysis, and natural language filtering powered by Google's Generative AI.

## Features

- Store and manage strings with their properties
- Calculate string metrics (length, word count, unique characters)
- Check for palindromes
- Generate SHA256 hashes
- Create character frequency maps
- Filter strings using various criteria
- Natural language filtering using AI

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Google AI API key (for natural language filtering)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd stage1
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```powershell
.\venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Set up your Google AI API key:
   - Open `gen_ai.py`
   - Replace `YOUR_API_KEY` with your actual Google AI API key

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. The API will be available at `http://localhost:5000`

## API Endpoints

### POST /strings
Add a new string to the collection.

**Request:**
```json
{
    "value": "hello world"
}
```

**Response (201 Created):**
```json
{
    "value": "hello world",
    "id": "hash...",
    "properties": {
        "length": 11,
        "is_palindrome": false,
        "unique_characters": 8,
        "word_count": 2,
        "sha256_hash": "hash...",
        "character_frequency_map": {
            "h": 1,
            "e": 1,
            "l": 3,
            "o": 2,
            "w": 1,
            "r": 1,
            "d": 1
        }
    },
    "created_at": "2025-10-21T10:00:00Z"
}
```

### GET /strings/{string_value}
Retrieve a specific string and its properties.

**Response (200 OK):**
```json
{
    "value": "level",
    "id": "hash...",
    "properties": {
        "length": 5,
        "is_palindrome": true,
        "unique_characters": 3,
        "word_count": 1,
        "sha256_hash": "hash...",
        "character_frequency_map": {
            "l": 2,
            "e": 2,
            "v": 1
        }
    },
    "created_at": "2025-10-21T10:00:00Z"
}
```

### GET /strings
Filter strings based on criteria.

**Query Parameters:**
- `is_palindrome` (boolean)
- `min_length` (integer)
- `max_length` (integer)
- `word_count` (integer)
- `contains_character` (string)

**Example:**
```
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
```

### GET /strings/filter-by-natural-language
Filter strings using natural language queries.

**Query Parameters:**
- `query` (string): Natural language description of desired filters

**Example:**
```
GET /strings/filter-by-natural-language?query=show me all palindromes with more than 5 characters
```

### DELETE /strings/{string_value}
Delete a specific string.

**Response (204 No Content)**

## Error Responses

- 400 Bad Request: Invalid input or missing required fields
- 404 Not Found: String not found
- 409 Conflict: String already exists
- 422 Unprocessable Entity: Invalid value type

## Testing

You can test the API using curl:

```bash
# 1. Add a string
curl -X POST http://localhost:5000/strings \
  -H "Content-Type: application/json" \
  -d '{"value":"hello world"}'

# 2. Get a specific string
curl -X GET http://localhost:5000/strings/hello%20world

# 3. Filter strings with criteria
curl -X GET "http://localhost:5000/strings?is_palindrome=true&min_length=5&max_length=20&word_count=2"

# 4. Natural language filtering
curl -X GET "http://localhost:5000/strings/filter-by-natural-language?query=show%20me%20all%20palindromes"

# 5. Delete a string
curl -X DELETE http://localhost:5000/strings/hello%20world

# Note: For Windows cmd.exe, use double quotes instead of single quotes:
curl -X POST http://localhost:5000/strings -H "Content-Type: application/json" -d "{\"value\":\"hello world\"}"
```

## License

[MIT License](LICENSE)