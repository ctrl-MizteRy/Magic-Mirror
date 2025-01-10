import gTTS

obj = gTTS(text="I am sorry, I could not quite hear what you said. Would you like to try it again?", lang= "en", slow=False)
obj.save("voice_records/no_message.mp3")
obj = gTTS(text="Give me a second to think of what you just said", lang="en", slow=False)
obj.save("voice_records/speaking_respone.mp3")
obj = gTTS(text="Yes, I am listening", lang="en", slow=False)
obj.save("voice_records/start_listen.mp3")