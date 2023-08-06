
import requests
import json


build_rig_adress = 'http://creaturecast-library.herokuapp.com/create_rig'
chunk_size = 8192


def create_rig(template_data):

    response = requests.post(build_rig_adress, data=template_data, headers={'Content-Type': 'application/json'})
    bytes_so_far = 0
    response_string = ''


    for chunk in response.iter_content(chunk_size):
        if not chunk:
            break
        response_string += chunk
        bytes_so_far += len(chunk)
        yield bytes_so_far

    response_data = json.loads(response_string)

    if not response_data['success']:
        raise Exception('Server Error.\n%s' % response_data['message'])

