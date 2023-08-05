import asyncio
import datetime
from argparse import ArgumentParser
from functools import partial

import requests
import qth

from .version import __version__


loop = asyncio.get_event_loop()
loop.set_debug(True)
client = None

prefix = "weather/stockport/"

api_key = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
latitude = 0.0000
longitude = 0.0000
units = "xxx"

interval = 900

def unix_to_local(unixtime):
    return datetime.datetime.fromtimestamp(unixtime).strftime(
        "%H:%M:%S")

async def update_weather():
    try:
        r = await loop.run_in_executor(
            None, requests.get,
            "https://api.darksky.net/forecast/{}/{},{}?units={}".format(
                api_key, latitude, longitude, units))
        weather = r.json()
        
        await asyncio.wait([
            client.set_property(prefix + "last-update",
                                unix_to_local(weather["currently"]["time"])),
            client.set_property(prefix + "last-update/unix", weather["currently"]["time"]),
            client.set_property(prefix + "precipitation",
                                [report["precipProbability"]
                                 for report in weather["hourly"]["data"]]),
            client.set_property(prefix + "temperature",
                                [report["temperature"]
                                 for report in weather["hourly"]["data"]]),
            client.set_property(prefix + "subjective-temperature",
                                [report["apparentTemperature"]
                                 for report in weather["hourly"]["data"]]),
            client.set_property(prefix + "cloud-cover",
                                [report["cloudCover"]
                                 for report in weather["hourly"]["data"]]),
            client.set_property(prefix + "sunrise",
                                unix_to_local(weather["daily"]["data"][0]["sunriseTime"])),
            client.set_property(prefix + "sunrise/unix",
                                weather["daily"]["data"][0]["sunriseTime"]),
            client.set_property(prefix + "sunset",
                                unix_to_local(weather["daily"]["data"][0]["sunsetTime"])),
            client.set_property(prefix + "sunset/unix",
                                weather["daily"]["data"][0]["sunsetTime"]),
        ], loop=loop)
    finally:
        loop.call_later(interval, partial(loop.create_task, update_weather()))

async def async_main():
    await asyncio.wait([
        client.register(prefix + "last-update",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Time of last update from Darksky.net. (hh:mm:ss)",
                        delete_on_unregister=True),
        client.register(prefix + "last-update/unix",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Time of last update from Darksky.net. (Unix time.)",
                        delete_on_unregister=True),
        client.register(prefix + "precipitation",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Hourly precipitation probability (0.0 - 1.0) forecasts starting 'now'.",
                        delete_on_unregister=True),
        client.register(prefix + "temperature",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Hourly temperature forecasts starting 'now'..",
                        delete_on_unregister=True),
        client.register(prefix + "subjective-temperature",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Hourly feels-like temperature forecasts starting 'now'..",
                        delete_on_unregister=True),
        client.register(prefix + "cloud-cover",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Hourly cloud cover (0.0 - 1.0) starting 'now'..",
                        delete_on_unregister=True),
        client.register(prefix + "sunrise",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Sunrise time today (hh:mm:ss).",
                        delete_on_unregister=True),
        client.register(prefix + "sunset",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Sunset time today (hh:mm:ss).",
                        delete_on_unregister=True),
        client.register(prefix + "sunrise/unix",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Unix-time of sunrise today.",
                        delete_on_unregister=True),
        client.register(prefix + "sunset/unix",
                        qth.PROPERTY_ONE_TO_MANY,
                        "Unix-time of sunset today.",
                        delete_on_unregister=True),
    ], loop=loop)
    
    await update_weather()

def main():
    parser = ArgumentParser(
        description="A service which reports weather forecasts from Darksky")
    parser.add_argument("apikey", help="Darksky.net API key")
    parser.add_argument("latitude", type=float,
                        help="Latitude of forecast location.")
    parser.add_argument("longitude", type=float,
                        help="Longitude of forecast location.")
    parser.add_argument("--prefix", "-p", default="weather/",
                        help="Prefix for all weather reporting properties "
                             "(default %(default)s).")
    parser.add_argument("--units", "-u", default="auto",
                        choices=["auto", "ca", "uk2", "windGust", "us", "si"],
                        help="Darksky.net unit type choice. "
                             "(default %(default)s).")
    parser.add_argument("--update-interval", "-i", default=900, type=float,
                        help="Update interval in seconds. "
                             "(default %(default)s).")
    
    parser.add_argument("--host", "-H", default=None,
                        help="Qth server hostname.")
    parser.add_argument("--port", "-P", default=None, type=int,
                        help="Qth server port.")
    parser.add_argument("--keepalive", "-K", default=10, type=int,
                        help="MQTT Keepalive interval (seconds).")
    parser.add_argument("--version", "-V", action="version",
                        version="%(prog)s {}".format(__version__))
    args = parser.parse_args()
    
    global client, prefix, api_key, longitude, latitude, units, interval
    
    client = qth.Client(
        "qth_darksky", "Weather forecasts for Qth from Darksky.net",
        loop=loop,
        host=args.host,
        port=args.port,
        keepalive=args.keepalive,
    )
    prefix = args.prefix
    api_key = args.apikey
    latitude = args.latitude
    longitude = args.longitude
    units = args.units
    interval = args.update_interval
    
    loop.run_until_complete(async_main())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # Don't crash on Ctrl+C
        pass
        
