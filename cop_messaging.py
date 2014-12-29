import base64, simplejson as json
from formating import *
from contextpy import *

pwd = "COP" * 8


def encode(data):
  enc = [chr((ord(c) + ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(data)]
  return base64.urlsafe_b64encode("".join(enc))

def decode(enc):
  dec = [chr((256 + ord(c) - ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(base64.urlsafe_b64decode(enc))]
  return "".join(dec)


send_v1 = layer("v1")
send_v2 = layer("v2")
send_v3 = layer("v3")
receive_v1 = layer("v1")
receive_v2 = layer("v2")
receive_v3 = layer("v3")

send_layers = {
  "v1": send_v1,
  "v2": send_v2,
  "v3": send_v3,
}


def receive_layer_from_payload(raw_payload):
  if raw_payload.startswith("{") and raw_payload.endswith("}"):
    return receive_v2
  elif ":" in raw_payload:
    return receive_v1
  else:
    return receive_v3

def add_send_layer(result):
  result["send_layer"] = send_layers.get(result["version"], send_v2)
  return result

# incoming message
@base
def from_string(raw_payload):
  return add_send_layer(json.loads(raw_payload))

@around(receive_v1)
def from_string(raw_payload):
  result = dict()
  result["method"], _, result["data"] = raw_payload.partition(":")
  result["version"] = "v1"
  result["data"] = remove_tags(result["data"])
  return add_send_layer(result)

@around(receive_v2)
def from_string(raw_payload):
  return proceed(raw_payload)

@around(receive_v3)
def from_string(raw_payload):
  return proceed(decode(raw_payload))


# outgoing message
@base
def to_string(method, data):
  return json.dumps({"method": method, "data": plain_to_smileys(data)})

@around(send_v1)
def to_string(method, data):
  return "%s:%s" %(method, smileys_to_plain(remove_tags(data)))

@around(send_v2)
def to_string(method, data):
  return proceed(method, data)

@around(send_v3)
def to_string(method, data):
  return encode(proceed(method, data))