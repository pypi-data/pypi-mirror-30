class Constants:

    def __init__(self):
        self.version = "0.1a"
        self.paste_url = "https://pastebin.com/api/api_post.php"
        self.user_url = "https://pastebin.com/api/api_login.php"
        self.raw_paste_url = "https://pastebin.com/api/api_raw.php"
        self.headers = {
            "X-Library": "PasteBunny %s " % self.version,
            "X-Language": "Python 3.6"
        }

    def get_paste_url(self):
        return self.paste_url

    def get_user_url(self):
        return self.user_url

    def get_raw_url(self):
        return self.raw_paste_url

    def get_headers(self):
        return self.headers


class Expiry:

    NEVER = "N"
    MINUTES_10 = "10M"
    HOUR = "1H"
    DAY = "1D"
    WEEK = "1W"
    WEEKS_2 = "2W"
    MONTH = "1M"
    MONTHS_6 = "6M"
    YEAR = "1Y"


class Privacy:

    PUBLIC = "0"
    UNLISTED = "1"
    PRIVATE = "2"


class Format:

    """
    I have a life, I don't plan to do this by myself
    """

    NAN = "text"
    PYTHON = "python"
    PHP = "php"
    PERL = "perl"
    RUBY = "ruby"
    JAVASCRIPT = "javascript"
    JAVA = "java"
