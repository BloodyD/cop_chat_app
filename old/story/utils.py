import re
from bbcode import Parser

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