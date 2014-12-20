import websocket, threading, time
import simplejson as json


wsuri = "ws://127.0.0.1:9000"
sock = None


class Client(object):
  def __init__(self):
    super(Client, self).__init__()
    self.connected = False
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
    method, _, content = message.partition(":")
    if method == "login":
      self.logged_in = True
      if content == "OK":
        print "You have logged in as %s!" %self.username
      else:
        print "Username %s already in use!" %self.username
    elif method == "chat":
      print content
    else:
      print "===================="
      print "MALFORMED MESSAGE: %s" %(message)
      print "===================="

  def send(self, message):
    if self.logged_in:
      self.ws.send("chat:%s"%message)
    else:
      self.username = message
      self.ws.send("login:%s"%message)

  def close(self):
    self.ws.close()
    self.ws_thread.join()


  def wait_until_connected(self):
    while not self.connected:
      time.sleep(1)

  def communicate(self):
    while True:
      message = raw_input("")
      if self.ws.sock is None: return
      self.send(message)


if __name__ == "__main__":
    # websocket.enableTrace(True)
    client = Client()

    client.wait_until_connected()
    try:
      client.communicate()
    except KeyboardInterrupt, e:
      client.close()
