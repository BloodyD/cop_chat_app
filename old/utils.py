from contextpy import layer
import simplejson as json, re
from bbcode import Parser


v1 = layer("Version 1")
v2 = layer("Version 2")
v3 = layer("Version 3")

is_anonymous = layer("Anonymous")


class Message(object):

  login = layer("Login")
  chat = layer("Chat")

  layer = None

  __method_to_layer = {
    "login": login,
    "chat": chat,
  }

  __version_to_layer = {
    "v1": v1,
    "v2": v2,
    "v3": v3,
  }
  def __init__(self, payload = None, data = None, method = None, version = "v2"):
    super(Message, self).__init__()
    if payload is None:
      self.data = data
      self.method = method
      self.version = version
    else:
      payload = json.loads(payload)
      self.data = remove_html(payload["data"])
      self.method = payload["method"]
      self.version = payload["version"]

  @property
  def version(self):
      return self._version

  @version.setter
  def version(self, value):
      self._version = self.__version_to_layer.get(value, v2)


  @property
  def method(self):
    return self._method

  @method.setter
  def method(self, value):
    self._method = value
    self.layer = self.__method_to_layer.get(value)

  def as_json(self):
    return json.dumps({"data": self.data, "method": self.method})


def remove_bbcode(data):
  return re.sub(r'\[[\/\.\:\w\s=\*\#]*\]\n{0,1}', "", data)

def remove_html(data):
  return re.sub(r'<[\/=\.\:\w\s\*\#\"\'\(\)]*>\n{0,1}', "", data)

def remove_tags(data):
  return remove_html(remove_bbcode(data))

def bbcode_to_html(data, *args, **kw):
  parser = Parser(*args, **kw)
  return parser.format(data)

media_replaces = [
  ["[img]", "<img src=\""],
  ["[/img]", "\">"],
  ["[font=", "<font face=\""],
  ["[size=50]", "<font size=\"1\">"],
  ["[size=85]", "<font size=\"2\">"],
  ["[size=100]", "<font size=\"3\">"],
  ["[size=150]", "<font size=\"4\">"],
  ["[size=200]", "<font size=\"5\">"],
  ["[/size]", "<font\">"],
  ["[/font]", "<font\">"],
  ["]", "\">"],
]

def bbcode_to_html_with_media(data):
  data = bbcode_to_html(data, escape_html = False, replace_links = False)
  return reduce(
    lambda data, replace: data.replace(*replace),
    media_replaces,
    data)