import base64
from formating import *

pwd = "COP" * 8

def encode(data):
  enc = [chr((ord(c) + ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(data)]
  return base64.urlsafe_b64encode("".join(enc))

def decode(enc):
  dec = [chr((256 + ord(c) - ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(base64.urlsafe_b64decode(enc))]
  return "".join(dec)

# outgoing message
def to_string(method, data, version = "v1"):
  if version == "v1":
    return "%s:%s" %(method, smileys_to_plain(remove_tags(data)))
  else:
    res = json.dumps({"method": method, "data": plain_to_smileys(data)})
    if version == "v3":
      return encode(res)
    return res

# incoming message
def from_string(raw_payload):
  try:
    return json.loads(raw_payload)
  except json.scanner.JSONDecodeError, e:
    try:
      return json.loads(decode(raw_payload))
    except json.scanner.JSONDecodeError, e:
      msg = {}
      msg["method"], _, msg["data"] = raw_payload.partition(":")
      msg["version"] = "v1"
      msg["data"] = remove_tags(msg["data"])
      return msg