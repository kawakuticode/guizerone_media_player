
import requests
import json
import demjson
from application.models.radio_station import Radio
from urllib.request import urlopen
from PIL import Image
from PIL.ImageQt import ImageQt
import io


local_url_api = " http://127.0.0.1:5000/api/v1/radios"
url_api = "https://angolawebapi.herokuapp.com/api/v1/radios"


class Network_util():

    @staticmethod
    def get_stations_from_api():
        try:
            response = requests.get(url_api)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print("server offline....")
        except requests.exceptions.ConnectionError as con:
            print("server offline....")

    @staticmethod
    def get_station_names(json_response):
        radio_encode = demjson.encode(json_response)
        stations_object = json.loads(radio_encode,
                                     object_hook=Radio.radio_decoder)
        return list(map(lambda x: x.r_name, stations_object))

    @staticmethod
    def get_station_obj(json_response):
        radio_encode = demjson.encode(json_response)
        return json.loads(radio_encode, object_hook=Radio.radio_decoder)

    @staticmethod
    def get_station_logo(station_url_logo):
        try:
            image = urlopen(station_url_logo)
            image_file = io.BytesIO(image.read())
            im = Image.open(image_file)
            qimage = ImageQt(im)
            return qimage
        except requests.exceptions.HTTPError as err:
            raise(err)
