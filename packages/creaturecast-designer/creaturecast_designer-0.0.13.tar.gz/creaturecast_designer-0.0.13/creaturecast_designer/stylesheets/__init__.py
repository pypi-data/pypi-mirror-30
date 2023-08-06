import os

stylesheets_directory = os.path.dirname(__file__.replace('\\', '/'))


def get_stylesheet(stylesheet_name):
    with open('%s/%s.css' % (stylesheets_directory, stylesheet_name), mode='r') as f:
        return f.read()
