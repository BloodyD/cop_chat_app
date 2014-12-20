import simplejson as json
from utils import *

from server_v1 import BaseClient as V1BaseClient, Server

class BaseClient(V1BaseClient):

  def __init__(self, *args, **kw):
    V1BaseClient.__init__(self, *args, **kw)
    self.version = None

  # client sends me a message
  def onMessage(self, payload, isBinary):
    payload = json.loads(payload)
    self.version = payload["version"]
    payload["data"] = bbcode_to_html(payload["data"], replace_links = False, escape_html = False)

    V1BaseClient.onMessage(self, json.dumps(payload), isBinary)


  # client will receive a message
  def sendMessage(self, content, method = "chat"):
    if self.version == "v1":
      content = remove_tags(content)

    V1BaseClient.sendMessage(self, content, method)