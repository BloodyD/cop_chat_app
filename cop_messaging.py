import base64, simplejson as json
from formating import *
from contextpy import *

pwd = "COP" * 8

v1 = layer("v1")
v2 = layer("v2")
encrypted = layer("encrypted")

layers = {
  "v1": v1,
  "v2": v2,
  "encrypted": encrypted,
}


def receive_layer_from_payload(raw_payload):
  if raw_payload.startswith("{") and raw_payload.endswith("}"):
    return [v2]
  else:
    return [v1]

def add_layer(result):
  result["layer"] = layers.get(result["version"], v2)
  return result


@base # v2 and v1
def encrypt(data):
  return data

@around(encrypted)
def encrypt(data):
  enc = [chr((ord(c) + ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(data)]
  return base64.urlsafe_b64encode("".join(enc))

@base # v2 and v1
def decrypt(enc):
  return enc

@around(encrypted)
def decrypt(enc):
  dec = [chr((256 + ord(c) - ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(base64.urlsafe_b64decode(enc))]
  return "".join(dec)

# incoming message
@base # v2
def from_string(raw_payload):
  return add_layer(json.loads(decrypt(raw_payload)))

@around(v1)
def from_string(raw_payload):
  result = dict()
  result["method"], _, result["data"] = decrypt(raw_payload).partition(":")
  result["version"] = "v1"
  result["data"] = remove_tags(result["data"])
  return add_layer(result)

# outgoing message
@base # v2
def to_string(method, data):
  return encrypt(json.dumps({"method": method, "data": plain_to_smileys(data)}))

@around(v1)
def to_string(method, data):
  return encrypt("%s:%s" %(method, smileys_to_plain(remove_tags(data))))
