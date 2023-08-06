import json
import time
import creaturecast_designer.services as svc
import requests
url=svc.library_url


def get_user_data(token, pause=0.1):
    while True:
        request = requests.get(
            '%s/get_user_data' % url,
            params=dict(
                token=token
            )
        )
        if request.ok:
            json_string = request.text
            response_data = json.loads(json_string)
            if response_data['status'] == 'succeeded':
                return response_data['data']
            else:
                print response_data['message']
                time.sleep(pause)
        else:
            print request.text
            print 'Failed with error code %s' % request.status_code
            return



if __name__ == '__main__':
    print get_user_data('Foo')
