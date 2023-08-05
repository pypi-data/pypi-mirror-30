import requests
from requests.auth import HTTPBasicAuth
import logging
import json
import re



class Builder(object):

  newMessages = []
  CurrentMessages = []
  CurrentUsers = []
  CurrentUser = 'Not Logged In'
  CurrentChat = "No Room Selected"
  myJid = ''
  _builtForum = {}
  _builtUsers = []
  _builtTopics = []
  _connectedTo = 'None'

  def __init__(self, params):
    self.username = params.get('email')
    self.password = params.get('password')
    self.org = params.get('org')
    self.jsondata = params.get('data')
    self.socketaddr = self.jsondata['d']['services']['chat']
    self.sessionid = self.jsondata['d']['sessionId']
    self.url = 'https://{}.ryver.com/api/1/odata.svc/'.format(self.org)
    Builder._connectedTo = 'https://{}.ryver.com'.format(self.org)
    #logging.debug(self.username)
    self.pullInfo()
    #logging.debug(Builder._builtForum)

  def pullInfo(self):
      self.ryverData = requests.get(self.url+'Ryver.Info()', auth=(self.username, self.password))
      self.ryverInfo = self.ryverData.json()
      self.user_build = self.createUserDict(self.ryverInfo)
      self.forum_build = self.createForumDict(self.ryverInfo)
      Builder._builtUsers = self.user_build
      Builder._builtForum = self.forum_build


  def createUserDict(self, info):
      Builder.CurrentUser = info['d']['me']['username']
      Builder.myJid = info['d']['me']['jid']
      self.users = []
      self.templist = info['d']['users']
      for i in self.templist:
          self._username = i['descriptor']
          # Make all usernames offline until we know otherwise via the websocket
          self.offlineUsername = '({})'.format(self._username)
          self.users.append({'username': self._username, 'jid': i['jid'], 'id': i['id'], 'usernameStatus': self.offlineUsername})

      return self.users


  def createForumDict(self, info):
      self.forums = {}
      self.frmlist = info['d']['forums']
      for i in self.frmlist:
          self.description = i['descriptor']
          self.forums[self.description] = ['forum', i['jid'], i['id']]
      self.wkgplist = info['d']['teams']
      for i in self.wkgplist:
          self.description = i['descriptor']
          self.forums[self.description] = ['wkgp', i['jid'], i['id']]
      return self.forums

  def changeRoom(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentUsers = []
      Builder.CurrentChat = identifier
      self._id = Builder._builtForum[identifier][2]
      self._width = width
      if Builder._builtForum[identifier][0] == 'forum':
        self._frmchatHistory(type='forums')
      elif Builder._builtForum[identifier][0] == 'wkgp':
        self._frmchatHistory(type='workrooms')

  def changeDm(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentUsers = []
      Builder.CurrentChat = identifier
      self._id = [x['id'] for x in self._builtUsers if x['username'] == identifier]
      self._id = self._id[0]
      self._width = width
      self._frmchatHistory(type='users')

  def _frmchatHistory(self, type):
      self._type = type
      self._params = {
          '$format': 'json',
          '$top': '25',
          '$orderby': 'when desc',
          '$inlinecount': 'allpages'
      }
      url = self.url+'{}({})/Chat.History()'.format(self._type, self._id)
      logging.debug(url)
      self._chatHistory = requests.get(url, params=self._params, auth=(self.username, self.password))
      self._chatInfo = self._chatHistory.json()
      self.temp = self._chatInfo['d']['results']
      for i in range(len(self.temp)-1, -1, -1):
          self._postTime = self.temp[i]['when']
          self._postTime = self._postTime.split('.', 1)[0]
          self._postTime = self._postTime.split('T', 1)[1]
          self._poster = self.temp[i]['from']['__descriptor']
          self._postMessage = self.temp[i]['body']
          self._originalMessage = '['+self._postTime+'] '+self._poster+': '+self._postMessage
          self._slicedMsg = self._chatSlicer(self._originalMessage, self._width)
          for x in self._slicedMsg:
              Builder.CurrentMessages.append(x)
      if self._type == 'forums' or self._type == 'workrooms':
          self._frmcurrentChatUsers()


  def _frmcurrentChatUsers(self):
      url = self.url+'{}({})/members'.format(self._type, self._id)
      self._userList = requests.get(url, auth=(self.username, self.password))
      self._userInfo = self._userList.json()
      self.temp = self._userInfo['d']['results']
      for i in range(0, len(self.temp)):
         for n in range(0, len(Builder._builtUsers)):
             if self.temp[i]['extras']['displayName'] == Builder._builtUsers[n]['username']:
                 Builder.CurrentUsers.append(Builder._builtUsers[n])

  def _topicListPuller(self, identifier):
      Builder._builtTopics = []
      self._id = Builder._builtForum[identifier][2]
      if Builder._builtForum[identifier][0] == 'forum':
        self._topicLists(type='forums')
      elif Builder._builtForum[identifier][0] == 'wkgp':
        self._topicLists(type='workrooms')

  def _topicLists(self, type):
      self._type = type
      self._params = {
          '$format': 'json',
          '$top': '30',
          '$orderby': 'modifyDate',
          '$inlinecount': 'allpages'
      }
      url = self.url+'{}({})/Post.Stream()'.format(self._type, self._id)
      self._topics = requests.get(url, params=self._params, auth=(self.username, self.password))
      self._topicInfo = self._topics.json()
      #logging.debug(self._topicInfo)
      self._topicInfo = self._topicInfo['d']['results']
      for i in range(len(self._topicInfo)):
          self._title = self._topicInfo[i]['subject']
          self._topicId = self._topicInfo[i]['id']
          Builder._builtTopics.append({'title': self._title, 'id': self._topicId})

  def _topicChatHistory(self, width):
      self._width = width
      self._topicId = [x['id'] for x in Builder._builtTopics if x['title'] == Builder.CurrentChat]
      self._topicId = self._topicId[0]
      self._params = {
          '$expand': 'createUser',
          '$select': 'id,comment,createDate,createUser,createUser/id',
          '$format': 'json',
          '$top': '25',
          '$filter': '((post/id eq '+str(self._topicId)+'))',
          '$orderby': 'createDate desc',
          '$inlinecount': 'allpages'

      }
      url = self.url+'postComments'
      self._topicChatReq = requests.get(url, params=self._params, auth=(self.username, self.password))
      self._topicChatInfo = self._topicChatReq.json()
      self._msgInfo = self._topicChatInfo['d']['results']
      #logging.debug(self._msgInfo[0])
      for i in range(len(self._msgInfo)-1, -1, -1):
          self._msgText = self._msgInfo[i]['comment']
          self._createTime = self._msgInfo[i]['createDate']
          self._createTime = self._createTime.split('+', 1)[0]
          self._createTime = self._createTime.split('T', 1)[1]
          self._msgUser = self._msgInfo[i]['createUser']['__descriptor']
          self._completeMsg = '['+self._createTime+'] '+self._msgUser+': '+self._msgText
          self._slicedMsg = self._chatSlicer(self._completeMsg, self._width)
          for x in self._slicedMsg:
              Builder.CurrentMessages.append(x)





  def _createTopic(self, channel, subject, body):
      try:
        if Builder._builtForum[channel][0] == 'forum':
            self._inType = 'Entity.Forum'
        elif Builder._builtForum[channel][0] == 'wkgp':
            self._inType = 'Entity.Workroom'
      except KeyError:
          logging.debug("invalid room")
          return
      self._channelId = Builder._builtForum[channel][2]
      self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      self._payload = {
          "subject": subject,
          "body": body,
          "outAssociations": {
              "results": [
                  {
                      "inId": self._channelId,
                      "inType": self._inType,
                      "inSecured": True,
                      "inName": channel
                  }
              ]
          },
          "recordType": "note"
      }
      url = self.url+'posts'
      self._createRequests = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), 
                                           data=json.dumps(self._payload), headers=self.headers)
      return self._createRequests


  def _chatSlicer(self, msg, width):
      self._sliced = []
      self._width = width
      self._workedMsg = msg
      if 'Pasted Image' in msg:
          self._sliced.append(msg)
          return self._sliced
      while len(self._workedMsg) > self._width:
          sectionOne = self._workedMsg[:self._width]
          sectionTwo = self._workedMsg[self._width:]
          try:
              sectionOne = sectionOne.rsplit(' ', 1)
              logging.debug(sectionOne)
              sectionTwo = sectionOne[1] + sectionTwo
              sectionOne.pop()
              self._sliced.append(sectionOne[0])
              self._workedMsg = sectionTwo
          except IndexError:
              logging.debug(
                  "No white space found, appending entire line. This usually occurs when someone pastes an image.")
              break
      self._sliced.append(self._workedMsg)
      return self._sliced

  @staticmethod
  def _status_order(x):
      return([re.findall(r'^\+', x['usernameStatus']), re.findall(r'^\-', x['usernameStatus']), re.findall(r'^\(x\)', x['usernameStatus'])])


