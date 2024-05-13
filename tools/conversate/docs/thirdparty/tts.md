API documentation
http://127.0.0.1:7860/
5 API endpoints

Use the gradio_client Python library or the @gradio/client Javascript package to query the demo via API.

copy
$ pip install gradio_client
Named Endpoints
api_name: /update_dropdown
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
							api_name="/update_dropdown"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		Rogger,	# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]]  in 'Select Speaker' Dropdown component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio_1
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio_1"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /handle_recorded_audio_2
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		https://github.com/gradio-app/gradio/raw/main/test/test_files/audio_sample.wav,	# filepath  in 'Record Your Voice' Audio component
		"Hello!!",	# str  in 'Add new Speaker' Textbox component
							api_name="/handle_recorded_audio_2"
)
print(result)
Return Type(s)
# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]] representing output in 'Select Speaker' Dropdown component
api_name: /gen_voice
copy
from gradio_client import Client

client = Client("http://127.0.0.1:7860/")
result = client.predict(
		"Hello!!",	# str  in 'Speechify this Text' Textbox component
		Rogger,	# Literal[Rogger, Wilford Brimley - Diabetes Commercial [Lg6tWLPl5Z0]]  in 'Select Speaker' Dropdown component
		0.1,	# float (numeric value between 0.1 and 1.99) in 'Speed' Slider component
		Arabic,	# Literal[Arabic, Chinese, Czech, Dutch, English, French, German, Hungarian, Italian, Japanese, Korean, Polish, Portuguese, Russian, Spanish, Turkish]  in 'Language/Accent' Dropdown component
							api_name="/gen_voice"
)
print(result)