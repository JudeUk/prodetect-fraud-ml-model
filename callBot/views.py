from django.shortcuts import render

# Create your views here.
import assembly as aai
from elevenlabs import generate,stream
from openai import OpenAi


class AI_Assistant:
   def __init__(self):
      aai.settings.api_key = 'API_KEY'
      self.openai_client = OpenAi()
      self.elevenlabs_api_key = "API_KEY"

      self.transcriber = None


        #Prompt
      self.full_transcript = [
         {"role":"system","content":"You are a customer care service agent at a Nigerian Bank. Be resourceful and efficient."},
         ]
      
      ####### Real Time Transcription with Assembly Ai

   def start_transcription(self):

        self.transcriber = aai.RealtimeTranscriber(
           
           sample_rate= 16000,
           on_data =  self.on_data,
           on_error= self.on_error,
           on_open = self.on_open,
           on_close = self.on_close,
           end_utterance_silence_threshold = 1000
           
        )

        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate = 1)
        self.transcriber.stream(microphone_stream)



   def stop_transcription(self):
         if self.transcriber:
            self.transcriber.close()
            self.transcriber = None
       



   def on_open(self,session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        # 
        return

   def on_data(self,transcript: aai.RealtimeTranscript):
       if not transcript.text:
            return

       if isinstance(transcript, aai.RealtimeFinalTranscript):
            #print(transcript.text, end="\r\n")
            self.generate_ai_response(transcript)
       else:
            print(transcript.text, end="\r")


   def on_error(self,error: aai.RealtimeError):
        print("An error occured:", error)


   def on_close(self):
        #print("Closing Session")
        return
   
   def generate_ai_response(self,transcript):

       self.stop_transcription()

       self.full_transcript.append({"role":"user","content":transcript.text})

       print("f\nPatient: {transcript.text}",end = "\r\n")

       response = self.openai_client.chat.completions.create(
           
           model = "gpt-3.5-turbo",
           messages = self.full_transcript

       )

       ai_response = response.choices[0].message.content

       self.generate_audio(ai_response)

       self.start_transcription()

