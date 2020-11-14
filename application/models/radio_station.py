from json import JSONEncoder


class Radio:
    def __init__(self, r_name, url, stream_link, img_logo):
        self.r_name = r_name
        self.url = url
        self.stream_link = stream_link
        self.img_logo = img_logo

    def __str__(self):
        return f"radio station(name: {self.r_name}, url: {self.url},stream_link: {self.stream_link},logo: {self.img_logo})"

    def __repr__(self):
        return "<Radio(name={self.r_name!r}, url={self.url!r},stream_link: {self.stream_link!r},img_logo: {self.img_logo!r}) > ".format(self=self)

    def radio_decoder(dct):
        if "id" in dct:
            return Radio(dct["r_name"], dct["url"],
                         dct["stream_link"], dct["img_logo"])
        return dct

    class RadioEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__
