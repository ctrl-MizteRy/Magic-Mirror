from gtts import gTTS
from playsound import playsound
from datetime import datetime

class Start_Speaking:
    def __init__(self, name: str = None):
        self.lang = "en"
    
    def first_greeting(self, name: str = None) -> None:   
        self.name = " " if name is None else name
        tod = ['Morning', 'Afternoon', 'Evening']
        current_time = datetime.now().hour
        text = ""
        match current_time:
            case 5 |6 |7 |8 |9 |10 |11:
                text = f"Good {tod[0]} {self.name}"
            case 12 |13 |14 |15 |16 |17:
                text = f"Good {tod[1]} {self.name}"
            case _:
                text = f"Good {tod[2]} {self.name}"
        
        self.normal_speed(text, "voice_records/greeting.mp3")
        self.speak("voice_records/greeting.mp3")

    def normal_speed(self, text: str, file_name: str) -> None:
        obj = gTTS(text=text, lang=self.lang, slow=False)
        if self.check_file(file_name):
            obj.save(file_name)
        else:
            raise TypeError("File name must be saved in form mp3 or wav")

    def slow_speed(self, text: str, file_name: str) -> None:
        obj = gTTS(text=text, lang= self.lang, slow=True)
        if self.check_file(file_name):
            obj.save(file_name)
        else:
            raise TypeError("File name must be saved in form mp3 or wav")

    def check_file(self, file_name: str) -> bool:
        file = file_name.split(".")[-1]
        return file == "mp3"
    
    def speak(self, file_name:str) -> None:
        if self.check_file(file_name):
            playsound(file_name)
        else:
            raise ValueError("Couldn't play a file with that name, perhaps check if the file exist or if the name is correct")
