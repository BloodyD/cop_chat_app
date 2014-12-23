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
                          WebSocketServerProtocol,\
                          listenWS

def remove_bbcode(data):
  return re.sub(r'\[[\/\.\:\w\s=\*\#]*\]\n{0,1}', "", data)

def remove_html(data):
  return re.sub(r'<[\/=\.\:\w\s\*\#\"\'\(\)]*>\n{0,1}', "", data)

def remove_tags(data):
  return remove_html(remove_bbcode(data))

class Message(object):

  @staticmethod
  def to_string(method, data, version = "v1"):
    if version == "v1":
      return "%s:%s" %(method, remove_tags(data))
    else:
      return json.dumps({"method": method, "data": data})

  @staticmethod
  def from_string(raw_payload):
    try:
      return json.loads(raw_payload)
    except json.scanner.JSONDecodeError, e:
      msg = {}
      msg["method"], _, msg["data"] = raw_payload.partition(":")
      msg["version"] = "v1"
      msg["data"] = remove_tags(msg["data"])
      return msg



class Handler(object, WebSocketServerProtocol):

  def __init__(self):
    object.__init__(self)
    self.username = None
    self.version = None

  def onOpen(self):
    self.server.register(self)

  def onClose(self, was_clean, code, reason):
    self.server.unregister(self)
    if self.username is not None:
      self.server.chat(self, "User %s logged out!" %self.username)
      self.username = None
    print "closed a connection!(%s, %d, %s)" %(str(was_clean), code, reason)

  def onMessage(self, payload, isBinary):
    msg = Message.from_string(payload)
    if msg["method"] == "login":
      if self.server.login(self, msg["data"]):
        self.username = msg["data"]
        self.version = msg["version"]
        self.sendMessage(Message.to_string("login", "OK", msg["version"]))
        self.server.chat(self, "User %s logged in!"%(self.username))
      else:
        self.sendMessage(Message.to_string("login", "Username %s already in use!" %msg["data"], msg["version"]))
    else:
      self.server.chat(self, "%s: %s" %(self.username, msg["data"]))

  def sendMessage(self, message):
    WebSocketServerProtocol.sendMessage(self, message.encode("utf-8"))

  # only for naming
  @property
  def server(self):
    return self.factory

  @server.setter
  def server(self, value):
    self.factory = value


class Server(WebSocketServerFactory):
  """
  Simple broadcast server broadcasting any message it receives to all
  currently connected clients.
  """

  def __init__(self, url, debug = False, debugCodePaths = False):
    WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
    self.handlers = set()

  register = lambda self, client_handler: self.handlers.add(client_handler)
  unregister = lambda self, client_handler: self.handlers.remove(client_handler)

  def login(self, client_handler, username):
    return username not in map(lambda handler: handler.username, self.handlers)

  def chat(self, client_handler, content):
    for handler in self.handlers:
      if client_handler == handler or handler.username is None: continue
      handler.sendMessage(Message.to_string("chat", " %s" %(content), handler.version))


if __name__ == '__main__':

  # log.startLogging(open("chat_server.log", "w"))
  log.startLogging(sys.stdout)
  debug = True

  server = Server("ws://localhost:9000",
                  debug = debug,
                  debugCodePaths = debug)

  server.protocol = Handler
  server.setProtocolOptions(allowHixie76 = True)
  listenWS(server)

  web = Site(File("."))
  reactor.listenTCP(8000, web)

  reactor.run()
