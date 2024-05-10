Conversate is an application that allows you to have a simple voice conversation with a locally running AI model. The flow is as follows: 

A simple user interface with a solid color background and a large circle of a complimtary color in the center. 
The color of the circle will indicate its status: orange for listening, purple for thinking, green for speaking, and blue for idle.
The spacebar will work like a PTT key: pressing it down will start the recording and releasing it will stop the recording. Recordings under 1 second will be discarded. 
The user's audio query will be converted to text using whisperx (see whisperx.md)
The query will be sent to a local language model api (see llm_api.md)
The response from the api will be spoken out loud using our tts api (see tts_api.md)
All interactions will be logged to a local sqlite database file called history

Ask any questions along the way.

Once everything is set up and ready to test, go ahead and start it up!

Create a readme file with an overview of the final project. 