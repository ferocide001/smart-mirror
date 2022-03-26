import json
from datetime import datetime
import pytz
import threading
import time

from channels.generic.websocket import WebsocketConsumer

from .widgets.time_feature import current_time
from .widgets.wetter_widget import WeatherWidget


class TimeConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.stop = False

        self.thread_time_display = threading.Thread(target=self.get_time)
        self.thread_time_display.start()

    def get_time(self):
        old_time = 0
        while True:
            time_query = datetime.now(pytz.timezone('Europe/Berlin'))
            current_time = time_query.strftime('%H:%M')
            day = time_query.strftime('%a')
            current_date = time_query.strftime(f'{day[0:2]} %d.%m.%Y')
            if current_time != old_time:
                self.send(json.dumps({
                    'time': str(current_time),
                    'date': str(current_date),
                }))
            old_time = current_time
            if self.stop:
                break

    def disconnect(self, code):
        self.stop = True
        del self.thread_time_display
        print('websocket disconntected')


class WeatherWidgetConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        f = open('main/config.json')
        config = json.load(f)
        api_key = config["weather_widget"]["api_key"]
        location = config["weather_widget"]["location"]
        self.stop = False
        weather_widget = WeatherWidget(
            api_key=api_key, location=location)
        self.thread_weather_widget = threading.Thread(
            target=self.get_weather, args=[weather_widget])
        self.thread_weather_widget.start()

    def get_weather(self, weather_widget):
        while True:
            weather_json = weather_widget.api_request()
            weather = weather_widget.format_request_small(weather_json)
            self.send(json.dumps(weather))
            if self.stop:
                break
            time.sleep(1200)

    def disconnect(self, code):
        self.stop = True
        del self.thread_weather_widget
        print('websocket disconntected')


class TimeWidgetConsumer(WebsocketConsumer):

    def connect(self):
        print('connected')
        self.accept()
        self.stop = False

        self.thread_time_widget = threading.Thread(target=self.get_time)
        self.thread_time_widget.start()

    def get_time(self):
        old_time = 0
        while True:
            cur_time = current_time()
            if cur_time != old_time:
                self.send(json.dumps({
                    'time': str(cur_time),
                }))
            old_time = cur_time
            if self.stop:
                break

    def disconnect(self, code):
        self.stop = True
        del self.thread_time_widget
        print('websocket disconntected')
