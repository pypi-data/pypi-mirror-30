class Paste:

    def __init__(self, code=None, name=None, _format=None, expiry=None, privacy=None, size=None, key=None, url=None, hits=None, expire_date=None, date=None):
        self.code = code
        self.name = name
        self.format = _format
        self.expiry = expiry
        self.privacy = privacy
        self.size = size
        self.key = key
        self.url = url
        self.hits = hits
        self.size = size
        self.expire_date = expire_date
        self.date = date
        if size is not None:
            self.size = int(size)
        if hits is not None:
            self.hits = int(hits)

    def set_code(self, text):
        self.code = text

    def set_name(self, name):
        self.name = name

    def set_format(self, _format):
        self.format = _format

    def set_expiry(self, expiry):
        self.expiry = expiry

    def set_privacy(self, privacy):
        self.privacy = privacy

    def set_size(self, size):
        self.size = size

    def set_key(self, key):
        self.key = key

    def set_url(self, url):
        self.url = url

    def set_hits(self, hits):
        self.hits = int(hits)

    def get_code(self):
        return self.code

    def get_name(self):
        return self.name

    def get_format(self):
        return self.format

    def get_expiry(self):
        return self.expiry

    def get_privacy(self):
        return self.privacy

    def get_size(self):
        return self.size

    def get_key(self):
        return self.key

    def get_url(self):
        return self.url

    def get_hits(self):
        return self.hits

    def __repr__(self):
        return "<Paste name=%s>" % self.name


class User:

    def __init__(self, name=None, avatar=None, website=None, email=None, location=None, _type=None):
        self.name = name
        self.avatar = avatar
        self.website = website
        self.email = email
        self.location = location
        if _type == 1:
            self.pro = True
        else:
            self.pro = False

    def get_name(self):
        return self.name

    def get_avatar_url(self):
        return self.avatar

    def get_website(self):
        return self.website

    def get_location(self):
        return self.location

    def get_account_type(self):
        if self.pro is True:
            return "PRO"
        return "REGULAR"

    def __repr__(self):
        return "<User %s [%s]>" % (self.name, self.get_account_type())


class PastebinException(Exception):
    ...
