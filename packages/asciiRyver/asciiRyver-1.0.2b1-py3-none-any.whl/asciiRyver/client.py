import websocket
import threading
import json
import logging
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from asciiRyver.framework import Builder



class Client(object):
  """
  Websocket Client object for a connection to Ryver.
  Initiated with parameters from loginview.py

  """


  def __init__(self, params, model):
    self.params = params
    self._model = model


  def _on_send(self, jid, msg):
      data = {'type': 'chat',
                   'text': msg,
                   'to': jid}
      self.ws.send(json.dumps(data))
      return

  def _send_topic(self, id, msg):
      data = {'comment': msg,
                   'post': {
                       'id': str(id)
                   }}
      headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      _sender = requests.post(self._baseurl+'postComments',
                                   auth=HTTPBasicAuth(self.username, self.password),
                                   data=json.dumps(data), headers=headers)



  def on_message(self, ws, message):
    self._message = json.loads(message)
    if self._message['type'] == 'chat':
        self._chatHandler()
    elif self._message['type'] == 'event':
        self._eventHandler()
    elif self._message['type'] == 'presence_change':
        self._presenceHandler()
    else:
      pass


  def on_error(self, ws, error):
    pass

  def on_close(self, ws):
    pass

  def on_open(self, ws):
      info = {'type': 'auth',
             'authorization': 'Session '+self.sessionid, 'agent': 'Ryver',
              'resource': 'Contatta-1516859178732'}
      self.ws.send(json.dumps(info))
      logging.debug('Connection established!')

  def run(self, params):
      self.username = params.get('email')
      self.password = params.get('password')
      self.org = params.get('org')
      self.jsondata = params.get('data')
      self.socketaddr = self.jsondata['d']['services']['chat']
      self.sessionid = self.jsondata['d']['sessionId']
      self._baseurl = 'https://{}.ryver.com/api/1/odata.svc/'.format(self.org)
      self.ws = websocket.WebSocketApp(self.socketaddr, on_message=self.on_message, on_error=self.on_error,
                                       on_close=self.on_close)
      self.ws.on_open = self.on_open
      self.t1 = threading.Thread(target=self.ws.run_forever)
      self.t1.daemon = True
      self.t1.start()

  def _presenceHandler(self):
      presenceKey = {'available': '+', 'away': '-', 'inactive': '-', 'dnd': '(x)'}
      _presence = self._message['presence']
      _fromJid = self._message['from']
      for i in range(0, len(Builder._builtUsers)):
          if Builder._builtUsers[i]['jid'] == _fromJid:
              originalName = Builder._builtUsers[i]['username']
              if _presence == 'unavailable':
                  originalName = '({})'.format(originalName)
                  Builder._builtUsers[i]['usernameStatus'] = originalName
              else:
                  Builder._builtUsers[i]['usernameStatus'] = presenceKey[_presence]+originalName
              self._model._signal.set()


  def _postHandler(self):
      currentChat = Builder.CurrentChat
      # See if current chat is in the Topics List
      if any(x['title'] == currentChat for x in Builder._builtTopics):
        postID = self._message['data']['created'][0]['postId']
        msgID = self._message['data']['created'][0]['id']
        currentid = [x['id'] for x in Builder._builtTopics if x['title'] == currentChat]
        currentid = currentid[0]
        if currentid == postID:
            params = {
                '$expand': 'createUser'
            }
            fullurl = self._baseurl+'postComments({})'.format(str(msgID))
            postComment = requests.get(fullurl, auth=(self.username, self.password), params=params)
            commentInfo = postComment.json()
            text = commentInfo['d']['results']['comment']
            postUser = commentInfo['d']['results']['createUser']['username']
            _time = datetime.now().strftime("%H:%M:%S")
            constructMsg = '[{}] {}: {}'.format(_time, postUser, text)
            self._model._messageQueue.append(constructMsg)
            self._model._signal.set()


  def _chatHandler(self):
      # DM Alerting needs reworking.
      myJid = Builder.myJid
      currentChat = Builder.CurrentChat
      if currentChat in Builder._builtForum.keys():
          # It's a forum/workgroup
          currentChatJid = Builder._builtForum[currentChat][1]
          if self._message['to'] == currentChatJid:
              self._messageFormatter()
          # Received a DM while not directly chatting in a forum/workgroup
          elif self._message['to'] == myJid:
              self._messageFormatter(dm=True)
      elif any(x['username'] == currentChat for x in Builder._builtUsers):
          # We are DM'ing a user
          currentUserJid = [x['jid'] for x in Builder._builtUsers if x['username'] == currentChat]
          currentUserJid = currentUserJid[0]
          # From our current user and directly to us
          if self._message['from'] == currentUserJid and self._message['to'] == myJid:
              self._messageFormatter()
          # From us to our current user
          elif self._message['from'] == myJid and self._message['to'] == currentUserJid:
              self._messageFormatter()
          # We received a DM from a user other than the one we are chatting with
          elif self._message['from'] != currentUserJid and self._message['to'] == myJid:
              self._messageFormatter(dm=True)
      elif any(x['title'] == currentChat for x in Builder._builtTopics):
          # We are in a Topic, but we still should know about DM's
          if self._message['to'] == myJid:
              self._messageFormatter(dm=True)
      else:
          pass



  def _messageFormatter(self, dm=False):
      try:
        text = self._message['text']
      except KeyError:
        text = ''
      fromJid = self._message['from']
      for i in range(0, len(Builder._builtUsers)):
          if Builder._builtUsers[i]['jid'] == fromJid:
              fromUser = Builder._builtUsers[i]['username']
      _time = datetime.now().strftime("%H:%M:%S")
      if dm:
          constructMsg = "*DM* [{}] {}: {}".format(_time, fromUser, text)
      else:
          constructMsg = "[{}] {}: {}".format(_time, fromUser, text)
      self._model._messageQueue.append(constructMsg)
      self._model._signal.set()

  def _eventHandler(self):
      if self._message['topic'] == "/api/activityfeed/postComments/changed":
          self._postHandler()
      else:
          pass

