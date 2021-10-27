from pyowm import OWM
import json
import pprint

owm = OWM('dc57f8d11379c7f3e5a213d7c1c19712')
mgr = owm.weather_manager()

def get_weather_data(user_lat, user_lon):
    one_call = mgr.one_call(lat=user_lat, lon=user_lon)
    current_data = (one_call.current.__dict__)
    return (current_data["humidity"],(current_data["temp"]["temp"] - 273.15))

print(get_weather_data(28.5355, 77.3910))