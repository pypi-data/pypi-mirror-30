import os
import json
import shutil
from os.path import expanduser
import creaturecast_designer

home_directory = expanduser("~").replace('\\', '/')
local_user = os.getenv('USER')
creaturecast_directory = '%s/creaturecast' % home_directory
home_environment_variables_path = '%s/environment_variables.json' % creaturecast_directory
package_directory = os.path.dirname(creaturecast_designer.__file__.replace('\\', '/'))
environment_variables_path = '%s/data/environment_variables.json' % package_directory
modules_directory = '%s/modules' % creaturecast_directory

data_cache = dict()


class Settings(object):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__()

    def __getitem__(self, item):
        return get_environment_variables()[item]

    def __setitem__(self, key, value):
        set_environment_variable(key, value)

    def get(self, *args):
        variables = get_environment_variables()
        if args[0] in variables:
            return variables[args[0]]
        elif len(args) > 1:
            return args[1]




settings = Settings()


def make_creaturecast_directory():
    if not os.path.exists(creaturecast_directory):
        os.makedirs(creaturecast_directory)

def make_environment_file():
    make_creaturecast_directory()
    if not os.path.exists(home_environment_variables_path):
        shutil.copyfile(environment_variables_path, home_environment_variables_path)

def get_environment_variables():
    make_environment_file()
    with open(home_environment_variables_path, mode='r') as f:
        return json.loads(f.read())

def set_environment_variable(key, value):
    variables = get_environment_variables()
    variables[key] = value
    with open(home_environment_variables_path, mode='w') as f:
        return f.write(json.dumps(variables))

def get_user_path(key):
    local_path = get_environment_variables().get(key, None)
    if not local_path:
        raise Exception('The user path "%s" was not found', key)
    return '%s%s' % (creaturecast_directory, local_path)


def get_data(key):
    if key in data_cache:
        return data_cache[key]
    home_path = copy_file_to_home_dir(key)
    with open(home_path, mode='r') as f:
        data = json.loads(f.read())
        data_cache[key] = data
        return data


def copy_file_to_home_dir(key):
    home_path = get_user_path(key)
    package_path = '%s/data/%s.json' % (package_directory, key)
    if not os.path.exists(home_path):
        shutil.copyfile(package_path, home_path)
    return home_path
