import websocket, thread, time
import simplejson as json

wsuri = "ws://127.0.0.1:9000"
sock = None



class Client(object):
    def disable_chat(self):
        pass

    def enable_chat(self):
        pass

    def chat(self, content): print content

    def on_message(self, ws, message):
        message = json.loads(message)
        if message["method"] == "login" and message["data"] == "OK":
            self.enable_chat()
        else:
            self.chat(message.data)

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "connection closed"
        self.ws = None
        self.disable_chat()

    def on_open(self, ws):
        print "connected to %s" %(wsuri)
        self.connected = True


    def __init__(self):
        super(Client, self).__init__()
        self.connected = False
        self.ws = websocket.WebSocketApp("ws://127.0.0.1:9000/",
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close)
        self.ws.on_open = self.on_open
        thread.start_new_thread(self.ws.run_forever, tuple())

    def send(self, message):
        if self.is_logged_in:
            self.login(message)
        else:
            self.ws.send(json.dumps({
                "method":"chat",
                "data":message,
                "version":"v1"}))

    def login(self, username):
        self.ws.send(json.dumps({
            "method":"login",
            "data":username,
            "version":"v1"}))

    @property
    def is_logged_in(self):
        pass

if __name__ == "__main__":
    websocket.enableTrace(True)
    client = Client()
    messages = {
        "login": "Enter a login name: ",
        "chat": "Chat: ",
    }
    while not client.connected:
        time.sleep(1)

    try:
        while True:
            client.send(raw_input(messages["login" if not client.is_logged_in else "chat"]))
    except KeyboardInterrupt, e:
        print "\nquiting the client"