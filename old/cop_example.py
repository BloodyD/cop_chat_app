from contextpy import *
import simplejson as json, base64

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


@base
def receive(payload):
  content = json.loads(payload)
  return content["method"], content["data"]

@base
def send(data):
  return json.dumps({"data": data, "method": "chat"})


@around(receive_v3)
def receive(payload):
  return proceed(decode(payload))

@around(receive_v2)
def receive(payload):
  return proceed(payload)

@around(receive_v1)
def receive(payload):
  return payload.split(":")


@around(send_v2)
def send(data):
  return proceed(data)

@around(send_v3)
def send(data):
  return encode(proceed(data))

@around(send_v1)
def send(data):
  return "chat:" + data


v1_content = "chat:Test1"
v2_content = json.dumps({"method": "chat", "data":"Test2"})
v3_content = encode(json.dumps({"method": "chat", "data":"Test3"}))

with activelayers(receive_v1, send_v1):
  method, data = receive(v1_content)
  print send(data)

with activelayers(receive_v1, send_v2):
  method, data = receive(v1_content)
  print send(data)

with activelayers(receive_v1, send_v3):
  method, data = receive(v1_content)
  print decode(send(data)), send(data)

print "==" * 20

with activelayers(receive_v2, send_v1):
  method, data = receive(v2_content)
  print send(data)

with activelayers(receive_v2, send_v2):
  method, data = receive(v2_content)
  print send(data)

with activelayers(receive_v2, send_v3):
  method, data = receive(v2_content)
  print decode(send(data)), send(data)

print "==" * 20

with activelayers(receive_v3, send_v1):
  method, data = receive(v3_content)
  print send(data)

with activelayers(receive_v3, send_v2):
  method, data = receive(v3_content)
  print send(data)

with activelayers(receive_v3, send_v3):
  method, data = receive(v3_content)
  print decode(send(data)), send(data)

