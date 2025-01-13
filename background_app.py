#!/usr/bin/env python3
from listening import Listening
from google_calendar import Google_Cal
from greeting import Start_Speaking
from weather import Weather_Report
from train_known_faces import Train_Faces
import cv2 as cv
import numpy as np
import face_recognition as fr
from concurrent.futures import ThreadPoolExecutor
import mediapipe as mp
import threading
import schedule
import time


class Magic_Mirror:
    def __init__(self):
        self.trainer = Train_Faces()
        self.cam = cv.VideoCapture(0)
        self.trainer.load_face_encoding('faces_encoding.pkl')
        self.known_people_encoding = self.trainer.get_people_encoding()
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands()

        #By using this, we could make the start up time faster and cv2 won't have to wait for the other classes to get their API request
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.init_calendar): "calendar",
                executor.submit(self.init_listen): "listen",
                executor.submit(self.init_speak): "speak",
                executor.submit(self.init_weather): "weather"
            }
        
        result = {}
        for future in futures:
            obj_name = futures[future]
            try:
                result[obj_name] = future.result()
            except Exception as e:
                print(f"Error happened {e}")
                exit(1)
        self.weather = result.get("weather")
        self.listen = result.get("listen")
        self.speak = result.get("speak")
        self.calendar = result.get("calendar")
        self.name = ""
        self.current_weather = self.weather.get_current()
        self.next_7_days = self.weather.get_7_days()
        self.today_events = self.calendar.get_today_events()
        threading.Thread(target= self.automatic_schedule, daemon=True).start()

    def start_recording(self):
        try:
            while True:
                ret, frame = self.cam.read()
                if not ret:
                    print("Could not find camera.")
                    exit(0)
                smaller_frame = cv.resize(frame, (0,0), fx=0.4, fy=0.4)
                vid = cv.cvtColor(smaller_frame, cv.COLOR_BGR2RGB)
                hand = self.hands.process(smaller_frame)
                unknown_encodings = fr.face_encodings(vid)
                if cv.waitKey(1) == ord('q'):
                    self.cam.release()
                    cv.destroyAllWindows()
                
                if unknown_encodings:
                    for encoding in unknown_encodings:
                        known_person_detected = False
                        for person_name, known_encodings in self.known_people_encoding.items():
                            for known_encoding in known_encodings.get_encodings():
                                distance = np.linalg.norm(known_encoding - encoding)
                                if distance < 0.6:
                                    known_person_detected = True
                                    if person_name == self.name:
                                        break
                                    else:
                                        self.speak.first_greeting(person_name)
                                        self.cam.release()
                                        self.cam = cv.VideoCapture(0)
                                        self.name = person_name
                                    break
                            if known_person_detected:
                                break
                        if not known_person_detected and self.name:
                            self.speak.first_greeting()
                            known_person_detected = True
                            self.name = ''
                            self.cam.release()
                            self.cam = cv.VideoCapture(0)

                    if hand.multi_hand_landmarks:
                        respone = self.listening(7)
                        self.handle_respone(respone)
                    
        except KeyboardInterrupt:
            self.cam.release()
            cv.destroyAllWindows()

    def listening(self, sec: int) -> set: #returning set for a faster time of string comparision
        while True:
            self.speak.speak("voice_records/start_listen.mp3")
            respone = self.listen.start_listen(sec)
            if not respone:
                self.speak.speak("voice_records/no_message.mp3")
                ans = self.listen.start_listen(2)
                ans = set(ans.split(" "))
                if 'yes' in ans or 'Yes' in ans:
                    continue
                else:
                    return {}
            else:
                respone = set(respone.split(" "))
                print(respone)
                return respone

    def handle_respone(self, respone: set) -> None:
        if respone: 
            if 'weather' in respone or 'temperature' in respone:
                if 'current' in respone:
                    self.speak.speak('voice_records/current_weather.mp3')
                elif 'today' in respone:
                    self.speak.speak('voice_records/hourly_weather.mp3')
                elif 'next' in respone or 'days' in respone:
                    self.speak.speak('voice_records/next_7_days_weather.mp3')
            elif ('calendar' in respone or 'schedule' in respone) and self.name: #checking for self.name so that an unknown person couldn't not get access to the calendar events, you can implement different set of name here if you want.
                if 'today' in respone:
                    self.speak.speak('voice_records/today_schedules.mp3')
                elif 'next' in respone or 'week' in respone:
                    self.speak.speak('voice_records/next_7_days_calendar.mp3')
                elif 'tomorrow' in respone:
                    self.speak.speak('voice_records/tomorrow_schedule.mp3')
        self.cam.release()
        self.cam = cv.VideoCapture(0)

    #Using schedule to update the data at a certain time for a faster respone time from gTTS text-to-speech
    def automatic_schedule(self):
        schedule.every().hour.do(self.weather.report_hourly_weather)
        schedule.every().day.at("00:00").do(self.calendar.today_events)
        schedule.every().day.at("00:05").do(self.calendar.tomorrow_events)
        schedule.every().day.at("00:10").do(self.calendar.next_7_days)
        schedule.every(30).minutes.do(self.weather.report_current_weather)
        schedule.every().day.at("00:20").do(self.weather.next_7_days_report)
        schedule.every(15).minutes.do(self.update_current_weather)
        schedule.every().day.at("00:25").do(self.update_7_days_weather)
        schedule.every().day.at("00:01").do(self.update_today_cal)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def update_current_weather(self) -> None:
        self.current_weather = self.weather.get_current()

    def update_7_days_weather(self) -> None:
        self.next_7_days = self.weather.get_7_days()

    def update_today_cal(self) -> None:
        self.today_events = self.calendar.get_today_events()

    def init_weather(self): 
        return Weather_Report()

    def init_speak(self):
        return Start_Speaking()

    def init_listen(self):
        return Listening()

    def init_calendar(self):
        return Google_Cal()
