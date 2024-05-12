from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from jnius import autoclass
import requests
# from dotenv import load_dotenv
import os

if platform == 'android':
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    Toast = autoclass('android.widget.Toast')

class QueryApp(App):
    def build(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Get the API password from the environment variable
        self.api_password = "lookatmeimanapikey"
        
        if not self.api_password:
            print("API password not found in the environment variables.")
            return
        
        # Create the main layout
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Create the text input field
        self.query_input = TextInput(multiline=False, size_hint=(1, None), height=50)
        layout.add_widget(self.query_input)
        
        # Create the submit button
        submit_button = Button(text='Submit', size_hint=(1, None), height=50)
        submit_button.bind(on_press=self.submit_query)
        layout.add_widget(submit_button)
        
        # Create the label to display the response
        self.response_label = Label(text='', size_hint=(1, None), height=200)
        layout.add_widget(self.response_label)
        
        if platform == 'android':
            self.register_ptt_receiver()
        
        return layout
    
    def register_ptt_receiver(self):
        self.ptt_receiver = PTTReceiver()
        
        intent_filter = IntentFilter()
        intent_filter.addAction('android.intent.PTT.up')
        intent_filter.addAction('android.intent.PTT.down')
        
        PythonActivity.mActivity.registerReceiver(self.ptt_receiver, intent_filter)
    
    def on_stop(self):
        if platform == 'android':
            PythonActivity.mActivity.unregisterReceiver(self.ptt_receiver)
        
        super().on_stop()
    
    def submit_query(self, instance):
        query_text = self.query_input.text
        
        if query_text:
            # Send the query to the API endpoint with password authentication
            response = requests.post('https://lumina.wayr.app/api/query', json={'query': query_text}, auth=('', self.api_password))
            
            if response.status_code == 200:
                data = response.json()
                short_answer = data.get('short_answer')
                
                if short_answer:
                    self.response_label.text = "Short Answer:\n" + short_answer
                else:
                    self.response_label.text = "No short answer available."
            else:
                self.response_label.text = "Error occurred while processing the query."
            
            # Clear the text input field
            self.query_input.text = ''
        else:
            self.response_label.text = "Please enter a query."

class PTTReceiver(PythonActivity):
    __javaclass__ = 'org.kivy.android.PTTReceiver'

    def __init__(self):
        super().__init__()
        self.toast = None
    
    def onReceive(self, context, intent):
        action = intent.getAction()
        
        if action == 'android.intent.PTT.up':
            message = 'PTT button released'
        elif action == 'android.intent.PTT.down':
            message = 'PTT button pressed'
        else:
            message = 'Unknown PTT action'
        
        if self.toast:
            self.toast.cancel()
        
        self.toast = Toast.makeText(context, message, Toast.LENGTH_SHORT)
        self.toast.show()
        
if __name__ == '__main__':
    QueryApp().run()