from contextlib import closing
import requests
import creaturecast_designer.services as svc

chunk_size = 24


def list_extensions():
    list_tools_url = '%s/list_extensions' % svc.library_url
    response = requests.get(list_tools_url, stream=True)
    if response.ok:
        with closing(response) as r:
            for line in svc.split_by_lines(r.iter_content(chunk_size)):
                if line:
                    yield line
    else:
        raise Exception(response.text)


if __name__ == '__main__':
    for x in list_extensions():
        print x
