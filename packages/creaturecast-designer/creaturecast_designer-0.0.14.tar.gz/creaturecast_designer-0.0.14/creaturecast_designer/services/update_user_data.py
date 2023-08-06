import json
import creaturecast_designer.services as svc
import requests
url = svc.library_url


def update_user_data(token, **kwargs):
    request = requests.post(
        '%s/update_user_data' % url,
        params=dict(
            token=token,
            data=kwargs
        )
    )
    if request.ok:
        json_string = request.text
        response_data = json.loads(json_string)
        if response_data['status'] == 'succeeded':
            return response_data['data']
        else:
            print response_data['message']
    else:
        print request.text
        print 'Failed with error code %s' % request.status_code
        return



