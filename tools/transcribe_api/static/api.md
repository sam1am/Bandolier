**API Endpoint Documentation**

**Endpoint:** `/transcribe`

**Method:** POST

**Description:**
This endpoint accepts an audio file and processes it, transcribing the content of the audio into text. This service is
used to convert speech from a WAV format audio file into text.

**Request:**
The request must be a multipart/form-data POST request. The audio file should be attached in the form field named
"file". The file should be in .wav format.

**Response:**
The response is a JSON object. Depending on the result of the transcription process, the response will have one of the
following formats:

1. If the transcription is successful, the JSON object will include a "transcription" field that contains a string of
   the transcribed audio.

````
{
"transcription": "<transcribed_text>"
    }
    ```

    2. If an error occurs during the transcription process, the JSON object will include an "error" field that describes
    what went wrong.

    ```
    {
    "error": "<error_description>"
        }
        ```

        **Possible HTTP response status codes:**

        - `200 OK`: The request was successful, and the response body contains the result of the transcription.

        - `400 Bad Request`: The request was invalid or cannot be served. The exact error is provided in the response
        body (e.g., `{"error": "No file uploaded"}`).

        - `500 Internal Server Error`: There was an error in performing the transcription. The exact error is provided
        in the response body.

        **Note:**
        Due to the complexity of the transcription process, there may be a considerable delay between the request and
        the response. Please remember to handle such conditions in your request management flow.
````
