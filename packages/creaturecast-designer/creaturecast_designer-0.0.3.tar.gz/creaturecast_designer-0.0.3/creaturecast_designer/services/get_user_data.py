import json
import time
import creaturecast_designer.services as services
from creaturecast_designer.extensions import requests

library_url = services.library_url

get_user_data_url = '%s/get_user_data' % library_url
chunk_size = 24


def get_user_data(temporary_pin, pause=0.0):
    while True:
        request = requests.get(
            get_user_data_url,
            params=dict(
                temporary_pin=temporary_pin
            )
        )
        json_string = request.text
        response_data = json.loads(json_string)
        if response_data['status'] == 'succeeded':
            return response_data['data']
        time.sleep(pause)



if __name__ == '__main__':
    print get_user_data('Foo')
