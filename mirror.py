import sys
import PyQt5
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QDateTime
from background_app import Magic_Mirror
import os
import threading
from pathlib import Path
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = os.fspath(Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins" / "platforms")
from datetime import datetime

class MagicMirror(QMainWindow):
    weekdays_map = ("Monday", "Tuesday", 
                   "Wednesday", "Thursday",
                   "Friday", "Saturday",
                   "Sunday")
    def __init__(self):
        super().__init__()
        self.mirror = Magic_Mirror()
        self.start_thread()
        self.init_ui()

    def start_thread(self):
        threading.Thread(target=self.mirror.start_recording, daemon=True).start()

    def init_ui(self):
        self.setWindowTitle("Magic Mirror")
        self.setGeometry(100, 100, 800, 480)
        self.setStyleSheet("background-color: black; color: gray;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(left_panel, 1)

        center_panel = QVBoxLayout()
        center_panel.setAlignment(Qt.AlignTop)
        main_layout.addLayout(center_panel)

        self.full_calendar_label = QLabel("Monthly Calendar")
        self.full_calendar_label.setFont(QFont("Arial", 35))
        self.full_calendar_label.setAlignment(Qt.AlignCenter)
        center_panel.addWidget(self.full_calendar_label)

        blank = "\n" *15
        self.calendar_label = QLabel(f"{blank}Today's Events:")
        self.calendar_label.setFont(QFont("Arial", 20))
        self.calendar_label.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(self.calendar_label)

        self.event_list = QLabel("Loading events...")
        self.event_list.setFont(QFont("Arial", 16))
        self.event_list.setAlignment(Qt.AlignLeft)
        left_panel.addWidget(self.event_list)

        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignRight)
        main_layout.addLayout(right_panel, 1)

        self.weather_label = QLabel("Loading weather...")
        self.weather_label.setFont(QFont("Arial", 20))
        self.weather_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.weather_label)

        self.weather_icon = QLabel()
        self.weather_icon.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.weather_icon)

        self.seven_day_forecast_layout = QVBoxLayout()
        self.seven_day_forecast_layout.setAlignment(Qt.AlignTop)

        self.forecast_grid = QGridLayout()
        self.forecast_grid.setSpacing(10)

        forecast_data = self.forecast_data()

        for i, data in enumerate(forecast_data):
            day_label = QLabel(data["day"])
            day_label.setFont(QFont("Arial", 16))
            day_label.setStyleSheet("color: gray;")
            day_label.setAlignment(Qt.AlignCenter)
            self.forecast_grid.addWidget(day_label, i, 0)

            icon_label = QLabel()
            pixmap = QPixmap(data["icon"])
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            self.forecast_grid.addWidget(icon_label, i, 1)


            temp_label = QLabel(f"{data['temp']}")
            temp_label.setFont(QFont("Arial", 14))
            temp_label.setStyleSheet("color: gray;")
            temp_label.setAlignment(Qt.AlignCenter)
            self.forecast_grid.addWidget(temp_label, i, 2)


        self.seven_day_forecast_layout.addLayout(self.forecast_grid)
        right_panel.addLayout(self.seven_day_forecast_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)

        self.update_weather()
        self.update_calendar()

    def forecast_data(self) -> list[dict]:
        forecast_data = []
        for i in range(7):
            data = dict()
            data['day'] = f"{self.weekdays_map[(datetime.weekday(datetime.today()) + i) % 7]}"
            data['temp'] = f"{round(self.mirror.next_7_days[2][i])}°F - {round(self.mirror.next_7_days[1][i])}°F"
            data['icon'] = self.weather_condition(int(self.mirror.next_7_days[8][i]))
            forecast_data.append(data)
        return forecast_data


    def update_clock(self) -> None:
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss A")
        current_date = QDateTime.currentDateTime().toString("dddd, MMMM d")
        self.full_calendar_label.setText(f"{current_date}\n{current_time}")

    def update_weather(self) -> None:
        temperature = f"{round((self.mirror.current_weather)[0])} °F"
        blank = "\n" *10
        self.weather_label.setText(f"{blank}Current Weather: {temperature}")
        pixmap = QPixmap(self.weather_condition(int((self.mirror.current_weather)[8])))
        pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.weather_icon.setPixmap(pixmap)

    def update_calendar(self):
        events = self.get_events()
        events_text = "\n".join(events)

        # Update the event list
        self.event_list.setText(events_text)
    def get_events(self) -> list[str]:
        events = self.mirror.today_events
        today_events = []
        for i in range(len(events[3])):
            today_events.append(f"{events[0][i]} - {events[1][i] if events[2][i] != " " else f"{events[2][i]}: {events[1][i]}"} - {events[3][i]}")

        return today_events
    

    def weather_condition(self, wmo: int) -> str:
        pic = "weather_icons/icons8-"
        match wmo:
            case 13:
                pic = pic + "cloud-lightning-100.png"
            case 0 | 1 | 3 | 19:
                pic = pic + "clouds-96.png"
            case x if 10 <= x <= 12 or 40 <= x <= 49 or x == 28:
                pic = pic + "fog-64.png"
            case x if 87 <= x <= 90 or x == 27:
                pic = pic + "hail-day-96.png"
            case 5:
                pic = pic + "haze-100.png"
            case 69 | 81 | 82 | 92:
                pic = pic + "heavy-rain-100.png"
            case 20 | 22 | 23 | 26 | 68 | 70 | 71:
                pic = pic + "light-snow-100.png"
            case 83 | 84 | 93:
                pic = pic + "sleet-96.png"
            case x if 1 <= x <= 3:
                pic = f"{pic}{"partly-cloudy-day-100.png" if 7 <= int(datetime.now().strftime("%H")) <= 18 else "night-96.png"}"
            case 6:
                pic = pic + "rain-cloud-100.png"
            case 73:
                pic = pic + "snow-96.png"
            case 94:
                pic = pic + "snow-storm-100.png"
            case x if 96 <= x <= 99:
                pic = pic + "stormy-weather-90.png"
            case 29:
                pic = pic + "storm-96.png"
            case 4:
                pic = pic + "wind-97.png"
            case 9:
                pic = pic + "wind-96.png"
            case _:
                pic = pic + "smiling-sun-96.png"
            
        return pic

def main():
    try:
        app = QApplication(sys.argv)
        window = MagicMirror()
        window.showFullScreen()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
        sys.exit(0)

if __name__ == "__main__":
    main()
