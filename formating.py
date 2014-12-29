import re

def remove_bbcode(data):
  return re.sub(r'\[[\/\.\:\w\s=\*\#]*\]\n{0,1}', "", data)

def remove_html(data):
  return re.sub(r'<[\/=\.\:\w\s\*\#\"\'\(\)]*>\n{0,1}', "", data)

def remove_tags(data):
  return remove_html(remove_bbcode(data))

smileys = [
  [u"\u263A", ":-)"],
]

def smileys_to_plain(data):
  return reduce(
    lambda data, replace: data.replace(*replace),
    smileys,
    data)

def plain_to_smileys(data):
  return reduce(
    lambda data, replace: data.replace(*reversed(replace)),
    smileys,
    data)
