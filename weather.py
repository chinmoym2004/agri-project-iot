from pyowm import OWM
import json
import pprint
import os,requests


owm = OWM(os.getenv("OPEN_WEATHER_API_KEY"))
mgr = owm.weather_manager()

def get_weather_data(lat, lon):
    one_call = mgr.one_call(lat=lat, lon=lon)
    current_data = (one_call.current.__dict__)
    return json.dumps(current_data);
    # weath_api = "https://api.openweathermap.org/data/2.5/weather"
    # final_url = weath_api + "?lat="+str(lat)+"&lon="+str(lon)+"&units=metric&appid="+os.getenv("OPEN_WEATHER_API_KEY")
    # weather_data = requests.get(final_url).json()
    # print(weather_data)
    # return weather_data['weather']