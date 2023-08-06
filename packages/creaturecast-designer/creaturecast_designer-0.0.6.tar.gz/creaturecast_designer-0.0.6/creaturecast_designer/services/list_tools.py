from contextlib import closing
import requests
import creaturecast_designer.services as services
library_url = services.library_url

list_tools_url = '%s/list_tools' % library_url
chunk_size = 24


def list_tools():
    with closing(requests.get(list_tools_url, stream=True)) as r:
        if r.status_code != 200:
            raise Exception(r.text)
        for line in services.split_by_lines(r.iter_content(chunk_size)):
            if line:
                yield line



if __name__ == '__main__':
    for x in list_tools():
        print x
