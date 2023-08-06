from requests import Session


class SiteSession(object):

    def __init__(self):
        self.session = Session()
