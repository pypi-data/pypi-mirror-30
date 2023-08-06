
import pip
import subprocess


def pip_install(package_name, version=None):
    # subprocess.check_output(['ls','-l']) #all that is technically needed...
    print subprocess.check_output(['pip', 'install', package_name])
    return package_name