Conversate API Specification
Base URL
The base URL for the API is not specified in the code. It should be set according to your deployment environment.

Authentication
The API uses HTTP Basic Authentication.

Username: Not specified (can be left blank)
Password: 'lookatmeimanapikey'
Endpoints
1. Query API
Endpoint: /api/query

Method: POST

Description: Sends a query to the Conversate system and receives a response.

Authentication Required: Yes

Request Body:

json
Copy code
{
  "query": "string"
}
Response:

json
Copy code
{
  "short_answer": "string"
}
Status Codes:

200: Successful response
400: Bad request (query text is missing)
401: Unauthorized (invalid credentials)
Example Request:

http
Copy code
POST /api/query HTTP/1.1
Host: your-api-host
Authorization: Basic bG9va2F0bWVpbWFuYXBpa2V5
Content-Type: application/json

{
  "query": "What's the weather like today?"
}
Example Response:

json
Copy code
{
  "short_answer": "The weather today is sunny with a high of 75°F (24°C)."
}
Notes
The API uses environment variables for configuration. Make sure to set these in your deployment environment:

MESSAGE_HISTORY: Number of previous messages to include for context (default: 10)
Other environment variables used in the backend (e.g., for LLM, TTS, and STT services)
The API interacts with a SQLite database to log interactions and retrieve message history.

The response processing includes extracting a "short_answer" from a JSON object within the LLM's response. If this fails, it falls back to the full response.

Error handling for database operations and LLM processing is not fully implemented in the provided code. Consider adding more robust error handling and appropriate error responses in a production environment.

The API is designed to work with a larger system that includes speech-to-text and text-to-speech capabilities, but these are not directly exposed through the API endpoint.

This specification covers the main /api/query endpoint exposed in the provided code. Expand this API as needed to expose additional functionality or to provide more detailed information about the system's state and capabilities.