import requests
from datetime import datetime
from dateutil import tz
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
    self._connectedTo = 'https://{}.ryver.com'.format(self.org)
    self.pullInfo()

  def pullInfo(self):
      ryverData = requests.get(self.url+'Ryver.Info()', auth=(self.username, self.password))
      ryverInfo = ryverData.json()
      self.user_build = self.createUserDict(ryverInfo)
      self.forum_build = self.createForumDict(ryverInfo)
      Builder._builtUsers = self.user_build
      Builder._builtForum = self.forum_build


  def createUserDict(self, info):
      Builder.CurrentUser = info['d']['me']['descriptor']
      Builder.myJid = info['d']['me']['jid']
      users = []
      templist = info['d']['users']
      for i in templist:
          username = i['descriptor']
          # Make all usernames offline until we know otherwise via the websocket
          offlineUsername = '({})'.format(username)
          users.append({'username': username, 'jid': i['jid'], 'id': i['id'], 'usernameStatus': offlineUsername, 'forums': [x['id'] for x in i['forums']], 'teams': [x['id'] for x in i['teams']]})
      return users


  def createForumDict(self, info):
      forums = {}
      frmlist = info['d']['forums']
      for i in frmlist:
          description = i['descriptor']
          forums[description] = ['forum', i['jid'], i['id']]
      wkgplist = info['d']['teams']
      for i in wkgplist:
          description = i['descriptor']
          forums[description] = ['wkgp', i['jid'], i['id']]
      return forums

  def changeRoom(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentChat = identifier
      _id = Builder._builtForum[identifier][2]
      self._width = width
      if Builder._builtForum[identifier][0] == 'forum':
        Builder.CurrentUsers = [i for i in self._builtUsers if _id in i['forums']]
        self._frmchatHistory(type='forums', id=_id)
      elif Builder._builtForum[identifier][0] == 'wkgp':
        Builder.CurrentUsers = [i for i in self._builtUsers if _id in i['teams']]
        self._frmchatHistory(type='workrooms', id=_id)

  def changeDm(self, identifier, width):
      Builder.CurrentMessages = []
      Builder.CurrentUsers = []
      Builder.CurrentChat = identifier
      _id = [x['id'] for x in self._builtUsers if x['username'] == identifier]
      _id = _id[0]
      self._width = width
      self._frmchatHistory(type='users', id=_id)

  def _frmchatHistory(self, type, id):
      _type = type
      _id = id
      _params = {
          '$format': 'json',
          '$top': '25',
          '$orderby': 'when desc',
          '$inlinecount': 'allpages'
      }
      url = self.url+'{}({})/Chat.History()'.format(_type, _id)
      _chatHistory = requests.get(url, params=_params, auth=(self.username, self.password))
      _chatInfo = _chatHistory.json()
      temp = _chatInfo['d']['results']
      timenow = datetime.now()
      utc_zone = tz.tzutc()
      local_zone = tz.tzlocal()
      timenow = timenow.astimezone(local_zone)
      for i in range(len(temp)-1, -1, -1):
          _poster = temp[i]['from']['__descriptor']
          _postMessage = temp[i]['body']
          _postTime = temp[i]['when']
          _postTime = _postTime.split('.')[0]
          _postTime = _postTime.replace('T', ' ')
          utcstamp = datetime.strptime(_postTime, "%Y-%m-%d %H:%M:%S")
          utcstamp = utcstamp.replace(tzinfo=utc_zone)
          localstamp = utcstamp.astimezone(local_zone)
          timediff = timenow - localstamp
          if timediff.days > 0:
              dateposted = localstamp.strftime('%m/%d')
              timeposted = localstamp.strftime('%H:%M:%S')
              _originalMessage = '({}) [{}] {}: {}'.format(dateposted, timeposted, _poster, _postMessage)
          else:
              timeposted = localstamp.strftime('%H:%M:%S')
              _originalMessage = '[{}] {}: {}'.format(timeposted, _poster, _postMessage)
          _slicedMsg = self._chatSlicer(_originalMessage, self._width)
          for x in _slicedMsg:
              Builder.CurrentMessages.append(x)

  def _topicListPuller(self, identifier):
      Builder._builtTopics = []
      _id = Builder._builtForum[identifier][2]
      if Builder._builtForum[identifier][0] == 'forum':
        self._topicLists(type='forums', id=_id)
      elif Builder._builtForum[identifier][0] == 'wkgp':
        self._topicLists(type='workrooms', id=_id)

  def _topicLists(self, type, id):
      _type = type
      _id = id
      _params = {
          '$format': 'json',
          '$top': '30',
          '$orderby': 'modifyDate',
          '$inlinecount': 'allpages'
      }
      url = self.url+'{}({})/Post.Stream()'.format(_type, _id)
      _topics = requests.get(url, params=_params, auth=(self.username, self.password))
      _topicInfo = _topics.json()
      _topicInfo = _topicInfo['d']['results']
      for i in range(len(_topicInfo)):
          _title = _topicInfo[i]['subject']
          _topicId = _topicInfo[i]['id']
          Builder._builtTopics.append({'title': _title, 'id': _topicId})

  def _topicChatHistory(self, width):
      self._width = width
      _topicId = [x['id'] for x in Builder._builtTopics if x['title'] == Builder.CurrentChat]
      _topicId = _topicId[0]
      _params = {
          '$expand': 'createUser',
          '$select': 'id,comment,createDate,createUser,createUser/id',
          '$format': 'json',
          '$top': '25',
          '$filter': '((post/id eq '+str(_topicId)+'))',
          '$orderby': 'createDate desc',
          '$inlinecount': 'allpages'

      }
      url = self.url+'postComments'
      _topicChatReq = requests.get(url, params=_params, auth=(self.username, self.password))
      _topicChatInfo = _topicChatReq.json()
      _msgInfo = _topicChatInfo['d']['results']
      timenow = datetime.now()
      utc_zone = tz.tzutc()
      local_zone = tz.tzlocal()
      timenow = timenow.astimezone(local_zone)
      for i in range(len(_msgInfo)-1, -1, -1):
          _msgUser = _msgInfo[i]['createUser']['__descriptor']
          _msgText = _msgInfo[i]['comment']
          _createTime = _msgInfo[i]['createDate']
          _createTime = _createTime.split('+', 1)[0]
          _createTime = _createTime.replace('T', ' ')
          utcstamp = datetime.strptime(_createTime, "%Y-%m-%d %H:%M:%S")
          utcstamp = utcstamp.replace(tzinfo=utc_zone)
          localstamp = utcstamp.astimezone(local_zone)
          timediff = timenow - localstamp
          if timediff.days > 0:
              dateposted = localstamp.strftime('%m/%d')
              timeposted = localstamp.strftime('%H:%M:%S')
              _completeMsg = '({}) [{}] {}: {}'.format(dateposted, timeposted, _msgUser, _msgText)
          else:
              timeposted = localstamp.strftime('%H:%M:%S')
              _completeMsg = '[{}] {}: {}'.format(timeposted, _msgUser, _msgText)
          _slicedMsg = self._chatSlicer(_completeMsg, self._width)
          for x in _slicedMsg:
              Builder.CurrentMessages.append(x)


  def _createTopic(self, channel, subject, body):
      try:
        if Builder._builtForum[channel][0] == 'forum':
            _inType = 'Entity.Forum'
        elif Builder._builtForum[channel][0] == 'wkgp':
            _inType = 'Entity.Workroom'
      except KeyError:
          return
      _channelId = Builder._builtForum[channel][2]
      headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
      _payload = {
          "subject": subject,
          "body": body,
          "outAssociations": {
              "results": [
                  {
                      "inId": _channelId,
                      "inType": _inType,
                      "inSecured": True,
                      "inName": channel
                  }
              ]
          },
          "recordType": "note"
      }
      url = self.url+'posts'
      _createRequests = requests.post(url, auth=HTTPBasicAuth(self.username, self.password), 
                                           data=json.dumps(_payload), headers=headers)
      return _createRequests


  def _chatSlicer(self, msg, width):
      _sliced = []
      self._width = width
      _workedMsg = msg
      if 'Pasted Image' in msg:
          _sliced.append(msg)
          return _sliced
      while len(_workedMsg) > self._width:
          sectionOne = _workedMsg[:self._width]
          sectionTwo = _workedMsg[self._width:]
          try:
              sectionOne = sectionOne.rsplit(' ', 1)
              sectionTwo = sectionOne[1] + sectionTwo
              sectionOne.pop()
              _sliced.append(sectionOne[0])
              _workedMsg = sectionTwo
          except IndexError:
              break
      _sliced.append(_workedMsg)
      return _sliced

  @staticmethod
  def _status_order(x):
      return([re.findall(r'^\+', x['usernameStatus']), re.findall(r'^\-', x['usernameStatus']), re.findall(r'^\(x\)', x['usernameStatus'])])


