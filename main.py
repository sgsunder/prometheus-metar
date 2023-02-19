import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import prometheus_client
import requests
from metar.Metar import Metar
from prometheus_client import Gauge

UPDATE_BUFFER_SEC = 300

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
wind_direction = Gauge("metar_wind_direction", "Wind Direction, in degrees", ["station"])
wind_speed = Gauge("metar_wind_speed", "Wind Speed, in m/s", ["station"])
visibility = Gauge("metar_visibility", "Visibility, in meters", ["station"])
temperature = Gauge("metar_temperature", "Temperature, in °C", ["station"])
dewpoint = Gauge("metar_dewpoint", "Dewpoint, in °C", ["station"])
barometer = Gauge("metar_barometer", "Barometric Pressure, in Pa", ["station"])


def update_metrics_for_station(station: str) -> datetime:
    response = requests.get(
        f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{station}.TXT"
    )
    response.raise_for_status()
    raw_metar = next(t for t in response.text.split("\n") if t.startswith(station))
    metar = Metar(raw_metar)

    wind_direction.labels(station=station).set(metar.wind_dir.value())
    wind_speed.labels(station=station).set(metar.wind_speed.value("MPS"))
    visibility.labels(station=station).set(metar.vis.value("M"))
    temperature.labels(station=station).set(metar.temp.value("C"))
    dewpoint.labels(station=station).set(metar.dewpt.value("C"))
    barometer.labels(station=station).set(metar.press.value("HPA") * 100)

    return metar.time


def station_daemon(station: str) -> None:
    while True:
        try:
            metar_update_time = update_metrics_for_station(station)
            next_update_time = metar_update_time + timedelta(hours=1)
            logger.info(f"Updated {station} on {metar_update_time.isoformat()}")
            wait_time = (next_update_time - datetime.utcnow()).total_seconds()
            if wait_time >= 0:
                sleep(wait_time)
        except Exception as e:
            # Ingore all errors
            logger.exception(e)
        finally:
            # Regardless of error status, sleep an additional buffer period
            # then try again
            sleep(UPDATE_BUFFER_SEC)


def main() -> None:
    parser = ArgumentParser(description="Run Prometheus endpoint for METAR data collection.")
    parser.add_argument("station", nargs="+", help="METAR station.")
    args = parser.parse_args()

    threads = [
        Thread(target=station_daemon, args=(station,), name=station)
        for station in args.station
    ]

    for thread in threads:
        thread.start()

    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)
    prometheus_client.start_http_server(port=3000)


if __name__ == "__main__":
    main()
