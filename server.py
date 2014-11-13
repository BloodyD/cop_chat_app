###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

# original source: https://github.com/tavendo/AutobahnPython/tree/master/examples/twisted/websocket/broadcast

import sys, simplejson as json, re

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                          WebSocketServerProtocol as BaseProtocol, \
                          listenWS

from contextpy import *

bbcode = layer("BBCode")
v1 = layer("Version 1")
v2 = layer("Version 2")
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
  }
  def __init__(self, payload = None, data = None, method = None, version = "v2"):
    super(Message, self).__init__()
    if payload is None:
      self.data = data
      self.method = method
      self.version = version
    else:
      payload = json.loads(payload)
      self.data = payload["data"]
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
  return re.sub(r'\[[\/\w\s=]*\]\n{0,1}', "", data)

def bbcode_to_html(data):
  return data.replace("[", "<").replace("]", ">")

class ClientProtocol(object, BaseProtocol):

  def __init__(self, *args, **kw):
    object.__init__(self)
    # self.logged_in = False
    self._username = None
    self.layers = set([is_anonymous])

  @property
  def logged_in(self):
    return self._username is not None

  @logged_in.setter
  def logged_in(self, value):
    pass # no setter!


  @property
  def username(self):
    return self._username

  @username.setter
  def username(self, val):
    self._username = val
    if val is not None:
      self.layers.remove(is_anonymous)
    else:
      self.layers.add(is_anonymous)

  # naming purpose
  @property
  def server(self):
    return self.factory

  @server.setter
  def server(self, value):
    self.factory = value


  def sendMessage(self, data, method = "chat"):
    print self.layers
    with activelayers(*self.layers):
      self._sendMessage(data, method)

  @base
  def _sendMessage(self, data, method):
    BaseProtocol.sendMessage(self, Message(data = data, method = method).as_json())

  @around(v2)
  def _sendMessage(self, data, method):
    proceed(bbcode_to_html(data), method)

  @around(v1)
  def _sendMessage(self, data, method):
    proceed(remove_bbcode(data), method)

  @around(is_anonymous)
  def _sendMessage(self, data, method):
    if method == "chat": return
    proceed(data, method)


  def onOpen(self):
    self.server.register(self)

  def onMessage(self, payload, isBinary):
    if isBinary: raise NotImplemented("Binary content is not supported!")
    m = Message(payload = payload)
    with activelayer(m.layer):
      with activelayers(*self.layers):
        self.handle_message(m)

  @base
  def handle_message(self, message):
    self.server.chat(message.data, self)

  @around(Message.login)
  # @around(is_anonymous)
  def handle_message(self, message):
    if not self.server.username_available(message.data):
      self.sendMessage("Username already in use!", method = "login")
      return

    self.username = message.data

    # set version layer
    self.layers.add(message.version)

    # inform the others
    self.server.inform("%s logged in!" %(self.username), exclude = self)

    # send info to self
    self.sendMessage("OK", method = "login")
    self.sendMessage("You are logged in!", method = "login")

  def logout(self):
    if not self.logged_in: return
    self.server.inform("%s logged out!" %(self.username), exclude = self)
    self.server.unregister(self)
    self.username = None

  def onClose(self, wasClean, code, reason):
    self.logout()

  def connectionLost(self, reason):
    self.logout()
    BaseProtocol.connectionLost(self, reason)


class Server(WebSocketServerFactory):
  """
  Simple broadcast server broadcasting any message it receives to all
  currently connected clients.
  """

  def __init__(self, url, debug = False, debugCodePaths = False):
    WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
    self._clients = set()

  register = lambda self, client: self._clients.add(client)
  unregister = lambda self, client: self._clients.remove(client)

  def clients(self, exclude = None):
    for c in self._clients:
      if exclude is None or exclude != c:
        yield c

  def username_available(self, username):
    return not any(map(lambda x: x.username == username, self.clients()))

  def inform(self, msg, exclude = None):
    for client in self.clients(exclude):
      client.sendMessage(msg, method = "inform")

  def chat(self, msg, sender):
    for client in self.clients():
      client.sendMessage("%s: %s" %(sender.username, msg))


if __name__ == '__main__':

  log.startLogging(sys.stdout)
  debug = True

  server = Server("ws://localhost:9000",
                  debug = debug,
                  debugCodePaths = debug)

  server.protocol = ClientProtocol
  server.setProtocolOptions(allowHixie76 = True)
  listenWS(server)

  webdir = File(".")
  web = Site(webdir)
  reactor.listenTCP(8080, web)

  reactor.run()
