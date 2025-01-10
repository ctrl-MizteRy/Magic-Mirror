import requests
from datetime  import datetime
from greeting import Start_Speaking


class Weather_Report:
    weekdays_map = ("Monday", "Tuesday", 
                   "Wednesday", "Thursday",
                   "Friday", "Saturday",
                   "Sunday")
    def __init__(self):
        self.get_api()
        self.speak = Start_Speaking()
        self.report_current_weather
        self.report_hourly_weather
        self.next_7_days_report

    def get_api(self):
        url = "https://api.open-meteo.com/v1/forecast?latitude=YOUR-LATITUDE-HERE&longitude=YOUR-LONGITUDE-HERE&current=temperature_2m,apparent_temperature,precipitation,rain,showers,snowfall,weather_code,wind_speed_10m&hourly=temperature_2m,apparent_temperature,rain,showers,snowfall,snow_depth,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,daylight_duration&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&timezone=America%2FChicago"
        re = requests.get(url = url)
        self.weather = re.json()

    def get_hourly(self):
        time = [(hours.split("-")[-1])[3:] for hours in self.weather['hourly']['time']]
        temperature_F = self.weather['hourly']['temperature_2m']
        feel_like_temp_f = self.weather['hourly']['apparent_temperature']
        wind_speed = self.weather['hourly']['wind_speed_10m']
        today_rain = self.weather['hourly']['rain'][:24]
        today_snowfall = self.weather['hourly']['snowfall'][:24]
        weather_code = self.weather['hourly']['weather_code'][:24]
        return [time, temperature_F, feel_like_temp_f, wind_speed, today_rain, today_snowfall, weather_code]
    
    def get_7_days(self):
        time = self.weather['daily']['time']
        max_temp = self.weather['daily']['temperature_2m_max']
        min_temp = self.weather['daily']['temperature_2m_min']
        feel_like_max = self.weather['daily']['apparent_temperature_max']
        feel_like_min = self.weather['daily']['apparent_temperature_min']
        sunrise = [(rise.split("-")[-1])[3:] for rise in self.weather['daily']['sunrise']]
        sunset = [(sunset.split("-")[-1])[3:] for sunset in self.weather['daily']['sunset']]
        daylight = [(sec / 3600) for sec in self.weather['daily']['daylight_duration']]
        weather_code = self.weather['daily']['weather_code']
        return [time, max_temp, min_temp, feel_like_max, feel_like_min, sunrise, sunset, daylight, weather_code]

    def get_current(self):
        temp = self.weather['current']['temperature_2m']
        feel_like_temp = self.weather['current']['apparent_temperature']
        wind_speed = self.weather['current']['wind_speed_10m']
        rain_mm = self.weather['current']['rain']
        snowfall_cm = self.weather['current']['snowfall']
        precipitation_mm = self.weather['current']['precipitation']
        sunrise = self.get_7_days()[5][1] #for the next day sunrise
        sunset = self.get_7_days()[6][0]    
        weather_code = self.weather['current']['weather_code']
        return [temp, feel_like_temp, wind_speed, rain_mm, snowfall_cm, precipitation_mm, sunrise, sunset, weather_code]

    def report_current_weather(self) -> None:
        report = self.get_current()
        current_report = ["Here's the current weather report:"]
        current_report.append(f"The temperature is {report[0]:.2f} degrees Fahrenheit, and it feels like {report[1]:.2f} degrees.")
        current_report.append(f"The wind is blowing at {report[2]:.2f} miles per hour.")

        if report[3] > 0:
            current_report.append(f"It is currently raining, with about {report[3]:.2f} inches of expected rainfall.")
        else:
            current_report.append("There is no rain at the moment.")

        if report[4] > 0:
            current_report.append(f"It is snowing outside, with about {report[4]:.2f} inches of expected snowfall.")
        else:
            current_report.append("And there is no snow at the moment.")

        if report[5] > 0:
            current_report.append(f"The total precipitation is {report[5]:.2f} inches.")
        
        hour, min = report[7].split(":")
        tmr_hour, tmr_min = report[6].split(":")
        current_report.append(f"The sun is expected to be setting today at {hour} hours and {min} minutes and won't be rising again until tomorrow around {tmr_hour} hours and {tmr_min} minutes.")
        text = " ".join(current_report)
        self.speak.normal_speed(text, "voice_records/current_weather.mp3")

    def report_hourly_weather(self) -> None:
        report = self.get_hourly()
        current_hour = datetime.now().hour
        remaining_hours = 25 - current_hour #Since indexing for hour start at 0
        time = report[0]
        temp = report[1]
        feel_like_temp = report[2]
        wind = report[3]
        rain = report[4]
        snow = report[5]
        low_temp, high_temp, strong_wind = temp[current_hour-1], temp[current_hour-1], wind[current_hour-1]
        low_temp_time, high_temp_time, wind_time = 0, 0, 0
        for i in range(remaining_hours, 24):
            if temp[i] < low_temp: 
                low_temp = temp[i]
                low_temp_time = i
            if temp[i] > high_temp: 
                high_temp = temp[i]
                high_temp_time = i
            if wind[i] > strong_wind :
                strong_wind = wind[i]
                wind_time = i
        text = (f"For the rest of the day, the coldest it will be is {low_temp} degree at around {time[low_temp_time]} and it feels like {feel_like_temp[low_temp_time]}"
                             f", the warmest it will be is {high_temp} degree at around {time[high_temp_time]} and it feels like {feel_like_temp[high_temp_time]}."
                             f" Wind speed will be the strongest at {time[wind_time]} with the speed of {strong_wind} miles per hour.")
        self.speak.normal_speed(text, "voice_records/hourly_weather.mp3")

    def next_7_days_report(self) -> None:
        report = self.get_7_days()
        max_temp = report[1]
        min_temp = report[2]
        feel_like_max = report[3]
        feel_like_min = report[4]
        daylight = report[7]

        days_reports = ["Here are the weathers for today and the next 6 days:"]
        for i in range(7):
            days_reports.append(f"On {self.weekdays_map[(datetime.weekday(datetime.today()) + i) % 7]},"
                                f" the highest temperature will be {max_temp[i]} degree, feeling like {feel_like_max[i]}. The lowest will be {min_temp[i]} degree, feeling like {feel_like_min[i]}."
                                f" Daylight will last for about {daylight[i]:1f} hours ")
        
        text = " ".join(days_reports)
        self.speak.normal_speed(text, "voice_records/next_7_days_weather.mp3")
    