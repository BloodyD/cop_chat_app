import websocket, threading, time, sys
import simplejson as json, base64
from os.path import basename


wsuri = "ws://127.0.0.1:9000"
sock = None
pwd = "COP" * 8



class Client(object):
  def __init__(self):
    super(Client, self).__init__()
    self.connected = False
    self.encrypted = False
    self.__encrypted = False
    self.ws = websocket.WebSocketApp(wsuri,
                              on_message = self.on_message,
                              on_error = self.on_error,
                              on_close = self.on_close)
    self.ws.on_open = self.on_open
    self.ws_thread = threading.Thread(target = self.ws.run_forever, args = tuple())
    self.ws_thread.start()

    self.logged_in = False
    self.username = ""

  def on_open(self, ws):
    print "connected to %s" %wsuri
    self.connected = True

  def on_close(self, ws):
    print "connection closed"
    self.close()

  def on_error(self, ws, error):
    raise error

  def on_message(self, ws, message):
    message = self.decrypt(message)
    method, _, content = message.partition(":")
    if method == "login":
      self.logged_in = True
      if content == "OK":
        self.encrypted = self.__encrypted
        print "You have logged in as %s!" %self.username
      else:
        print content
        exit()
    elif method == "chat":
      print content.decode("utf8").encode(sys.stdout.encoding)
    else:
      print "===================="
      print "MALFORMED MESSAGE: %s" %(message)
      print "===================="
      exit()

  def encrypt(self, data):
    if self.encrypted:
      enc = [chr((ord(c) + ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(data)]
      return base64.urlsafe_b64encode("".join(enc))
    else: return data

  def decrypt(self, enc):
    if self.encrypted:
      dec = [chr((256 + ord(c) - ord(pwd[i % len(pwd)])) % 256) for i, c in enumerate(base64.urlsafe_b64decode(enc))]
      return "".join(dec)
    else: return enc

  def send(self, message):
    if self.logged_in:
      self.ws.send(self.encrypt("chat:%s"%message))

  def close(self):
    self.ws.close()
    self.ws_thread.join()


  def wait_until_connected(self):
    while not self.connected:
      time.sleep(1)

  def communicate(self, username, encrypted):
    self.username = username
    self.ws.send("login:%s"%username)

    if encrypted:
      self.ws.send("encrypt:True")

    self.__encrypted = encrypted
    while True:
      message = raw_input("").decode(sys.stdin.encoding).encode("utf8")
      if self.ws.sock is None: return
      self.send(message)


if __name__ == "__main__":
  if len(sys.argv) < 2:
    opt1 = "python %s <username>" %(basename(sys.argv[0]))
    opt2 = "python %s <username> safe" %(basename(sys.argv[0]))
    print "usage:\n\t" + opt1 + "\n\t" + opt2
    exit()

  username = sys.argv[1]
  if not username:
    print "please enter non empty username!"
    exit()

  if len(sys.argv)== 3 and sys.argv[2] != "safe":
    print "please enter either \"safe\" or nothing for encrypted communication!"
    exit()


  # websocket.enableTrace(True)
  client = Client()

  client.wait_until_connected()
  try:
    encrypted = len(sys.argv) == 3
    client.communicate(username, encrypted)
  except KeyboardInterrupt, e:
    client.close()
