import os


# Create your views here.

import assemblyai as aai
from elevenlabs import generate,stream
from openai import OpenAI


class AI_Assistant:
   def __init__(self):
      self.ASSEMBLY_AI_API_KEY= os.getenv('aai.settings.api_key')
      self.OPEN_API_KEY = os.getenv('OPENAI_API_KEY')
      self.openai_client = OpenAI(api_key = "self.OPEN_API_KEY")
      self.ELEVENLABS_API_KEY = os.getenv('eleven_labs_api_key')

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

       print("f\nPatient or user: {transcript.text}",end = "\r\n")

       response = self.openai_client.chat.completions.create(
           
           model = "gpt-3.5-turbo",
           messages = self.full_transcript

       )

       ai_response = response.choices[0].message.content

       self.generate_audio(ai_response)

       self.start_transcription()



   def generate_audio(self,text):
          
          self.full_transcript.append({"role":"assistant","content":text})

          print(f"\nAI Receptionist or ai assistant: {text}")

          audio_stream = generate(
               
               api_key = self.ELEVENLABS_API_KEY,
               text = text,
               voice = "Alice",
               stream = True
          )

          stream(audio_stream)


greeting = "Thank you for calling Ecobank International. My name is Precious, how may i help you today"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()



