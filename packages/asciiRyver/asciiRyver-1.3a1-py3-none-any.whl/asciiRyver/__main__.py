from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Text, TextBox, Divider, Widget, Frame, Layout, Label, MultiColumnListBox, Button, PopUpDialog
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from asciiRyver.framework import Builder
from asciiRyver.client import Client
import sys
import logging
import requests
import threading
import time
import re

class Model(object):
    def __init__(self):
        self.running = object
        self.activeClient = object
        self._signal = threading.Event()
        self._messageQueue = []

class NewTopic(Frame):
    def __init__(self, screen, builder, model, colors):
        super(NewTopic, self).__init__(screen,
                                       screen.height * 2 // 3,
                                       screen.width * 2 // 3,
                                       title="New Topic")
        self.palette = colors
        self.model = model
        self._builder = builder
        self.layout = Layout([100], fill_frame=True)
        self.add_layout(self.layout)
        self.layout.add_widget(Text("Channel:", 'channel'))
        self.layout.add_widget(Text("Subject:", 'subject'))
        self.layout.add_widget(Text("Body:", 'body'))
        self.button_bar = Layout([1, 1, 1, 1])
        self.add_layout(self.button_bar)
        self.button_bar.add_widget(Button("OK", on_click=self._ok), 1)
        self.button_bar.add_widget(Button("Cancel", on_click=self._cancel), 2)
        self.fix()

    def _ok(self):
        self.save()
        self._topicCreate = self.model.running._createTopic(self.data['channel'],
                                                            self.data['subject'],
                                                            self.data['body'])
        logging.debug(self._topicCreate)
        try:
            if self._topicCreate.status_code == 201:
                raise NextScene("TopicPanel")
            else:
                self._scene.add_effect(PopUpDialog(self.screen, "Topic Creation Failed! HTTP Code: "+str(self._topicCreate.status_code), "X", on_close=None))
        except AttributeError:
            self._scene.add_effect(PopUpDialog(self.screen, "Topic Creation Failed! NOTE: Channel field is case sensitive!", "X", on_close=None))

    def _cancel(self):
        raise NextScene('TopicPanel')

class TopicPanel(Frame):
    def __init__(self, screen, builder, model, colors):
        super(TopicPanel, self).__init__(screen,
                                         screen.height * 2 // 3,
                                         screen.width * 2 // 3,
                                         on_load=self.reload,
                                         title="Topics")
        self.palette = colors
        self.model = model
        self._builder = builder
        self.layout = Layout([45, 5, 45], fill_frame=True)
        self.add_layout(self.layout)
        self._Channels = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Channelslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Channels, on_select=self._retrieveTopics)
        self.layout.add_widget(self._Channelslist, 0)
        self._Topics = [([x['title']], i) for i, x in enumerate(self._builder._builtTopics)]
        self._TopicsList = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Topics, on_select=self._joinTopic)
        self.layout.add_widget(self._TopicsList, 2)
        self.divideBox = Layout([100])
        self.add_layout(self.divideBox)
        self.divideBox.add_widget(Divider())
        self.buttonBox = Layout([50, 50])
        self.add_layout(self.buttonBox)
        self.buttonBox.add_widget(Button('Create New', on_click=self._newTopic), 0)
        self.buttonBox.add_widget(Button('Back', on_click=self._goBack), 1)
        self.fix()

    def _goBack(self):
        raise NextScene('Main')

    def _newTopic(self):
        raise NextScene('NewTopic')

    def _joinTopic(self):
        self._topicName = self._TopicsList.options[self._TopicsList.value][0][0]
        self._builder.CurrentChat = self._topicName
        self._builder.CurrentMessages = []
        self.model.running._topicChatHistory(myTest.chatWidth)
        raise NextScene("Main")

    def _retrieveTopics(self):
        self._channel = self._Channelslist.options[self._Channelslist.value][0][0]
        logging.debug("Fetching topics for "+self._channel)
        self.model.running._topicListPuller(self._channel)
        self.reload()


    def reload(self):
        self._Channelslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._TopicsList.options = [([x['title']], i) for i, x in enumerate(self._builder._builtTopics)]



class LoginView(Frame):

    def __init__(self, screen, builder, model, client, colors):
        super(LoginView, self).__init__(screen,
                                        screen.height * 2 // 3,
                                        screen.width * 2 // 3,
                                        title="Login")
        self.palette = colors
        self.model = model
        self._builder = builder
        self._client = client
        self.layout = Layout([100], fill_frame=True)
        self.add_layout(self.layout)
        self.layout.add_widget(Text("Email:", "email"))
        self.layout.add_widget(Text("Password:", "password", hide_char='*'))
        self.layout.add_widget(Text("Ryver Organization:", "organization"))
        self.button_bar = Layout([1, 1, 1, 1])
        self.add_layout(self.button_bar)
        self.button_bar.add_widget(Button("OK", on_click=self._ok), 0)
        self.button_bar.add_widget(Button("Cancel", on_click=self._cancel), 3)
        self.fix()

    def _ok(self):
        self.save()
        self.loginRequest = requests.post('https://'+self.data['organization']+'.ryver.com/api/1/odata.svc/User.Login()',
                                          auth=(self.data['email'], self.data['password']))
        if self.loginRequest.status_code == 200:
            # Success
            self.response = self.loginRequest.json()
            self.payload = {'email': self.data['email'], 'password': self.data['password'],
                       'org': self.data['organization'], 'data': self.response}
            self._builder(self.payload)
            self.model.running = self._builder(self.payload)
            self.newClient = self._client(self.payload, self.model)
            self.newClient.run(self.payload)
            self.model.activeClient = self.newClient
            raise NextScene("Main")
        else:
            self._scene.add_effect(PopUpDialog(self.screen, "Login Failed!", "X", on_close=None))

    def _cancel(self):
        raise NextScene("Main")


class myTest(Frame):

    chatWidth = int

    def __init__(self, screen, builder, model, colors):
        super(myTest, self).__init__(screen,
                                     int(screen.height * 3 // 3),
                                     int(screen.width * 3 // 3),
                                     has_border=False,
                                     on_load=self.reload
                                     )


        self.palette = colors
        self._model = model
        self._screen = screen
        self._builder = builder
        # Header
        self.layout = Layout([1])
        self.add_layout(self.layout)
        self._header0 = TextBox(1, as_string=True)
        self._header0.disabled = True
        self._header0.custom_colour = 'header'
        self._header0.value = "Connected to: {} | User: {} | Currnet Chat: {}".format(self._builder._connectedTo, self._builder.CurrentUser, self._builder.CurrentChat)
        self.layout.add_widget(self._header0, 0)

        # Main Chat Section
        self.mainBody = Layout([12, 2, 72, 2, 12], fill_frame=True)
        self.add_layout(self.mainBody)
        # Forum Column
        self._Forums = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Forumslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Forums, on_select=self._changeRoom)
        self.mainBody.add_widget(self._Forumslist, 0)
        # Messages Column
        self._Messages = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._Messageslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Messages)
        self.mainBody.add_widget(self._Messageslist, 2)
        # Users Column
        self._Users = [([x['usernameStatus']], i) for i, x in enumerate(self._builder._builtUsers)]
        self._Userslist = MultiColumnListBox(Widget.FILL_FRAME, [0], self._Users, on_select=self._changeUser)
        self.mainBody.add_widget(self._Userslist, 4)

        # Bottom Divider
        self.divideBox2 = Layout([1])
        self._footer = TextBox(1, as_string=True)
        self._footer.disabled = True
        self._footer.custom_colour = 'header'
        self._footer.value = "Use 'ctrl + l' to access the login menu, 'ctrl + t' for the topic menu, and 'ctrl + c' to quit."
        self.add_layout(self.divideBox2)
        self.divideBox2.add_widget(self._footer)

        # User Send Box
        self._chatCrt = TextBox(1, as_string=True)
        self._chatCrt.disabled = True
        self._chatCrt.value = '[Msg]:'
        self._MsgBox = TextBox(1, name='userMsg')
        self.sendBox = Layout([6, 87, 7])
        self.add_layout(self.sendBox)
        self.sendBox.add_widget(self._chatCrt, 0)
        self.sendBox.add_widget(self._MsgBox, 1)
        self.sendBox.add_widget(Button('Send', on_click=self._sendMsg), 2)
        self.fix()
        myTest.chatWidth = self._Messageslist._get_width(0)


    def process_event(self, event):
        if isinstance(event, KeyboardEvent):
            if event.key_code == Screen.ctrl('t'):
                raise NextScene("TopicPanel")
            elif event.key_code == Screen.ctrl('l'):
                raise NextScene("LoginForm")
            elif event.key_code == Screen.ctrl('c') or event.key_code == Screen.ctrl('q'):
                raise StopApplication("User quit.")
            else:
                pass
        else:
            pass
        return super(myTest, self).process_event(event)

    def _sendMsg(self):
        self.save()
        self.to = self._builder.CurrentChat
        # Check if we are in a topic
        if any(x['title'] == self.to for x in self._builder._builtTopics):
            self._id = [x['id'] for x in self._builder._builtTopics if x['title'] == self.to]
            self._id = self._id[0]
            self._model.activeClient._send_topic(self._id, self.data['userMsg'][0])
        # Check if we are in a forum/workgroup
        elif self.to in self._builder._builtForum.keys():
            self.toJid = self._builder._builtForum[self.to][1]
            self._model.activeClient._on_send(self.toJid, self.data['userMsg'][0])
        # Check if we are DM'ing
        elif any(x['username'] == self.to for x in self._builder._builtUsers):
            self.toJid = [x['jid'] for x in self._builder._builtUsers if x['username'] == self.to]
            self.toJid = self.toJid[0]
            self._model.activeClient._on_send(self.toJid, self.data['userMsg'][0])
        self._MsgBox.value = None
        self._MsgBox.focus()


    def _changeRoom(self):
        self._newRoom = self._Forumslist.options[self._Forumslist.value][0][0]
        logging.debug("Changing rooms to: "+self._newRoom)
        self._textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeRoom(self._newRoom, self._textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._usersSorted = sorted(self._builder.CurrentUsers, key=self._builder._status_order, reverse=True)
        self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(self._usersSorted)]
        self._builder.CurrentChat = self._newRoom

    def _changeUser(self):
        self._newUser = self._Userslist.options[self._Userslist.value][0][0]
        self._newUser = re.sub(r'[^A-Za-z0-9\s]', '', self._newUser)
        self._textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeDm(self._newUser, self._textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._builder.CurrentChat = self._newRoom

    def _chatFeeder(self):
        while True:
            time.sleep(0.1)
            self._model._signal.wait()
            if len(self._model._messageQueue) > 0:
                for i in self._model._messageQueue:
                    self._textBoxWidth = self._Messageslist._get_width(0)
                    self._sliced = self._model.running._chatSlicer(i, self._textBoxWidth)
                    for i in self._sliced:
                        self._num = len(self._Messageslist.options)
                        self._Messageslist.options.append(([i], self._num))
                        self._Messageslist.start_line = len(self._Messageslist.options)
                        self._Messageslist._line = len(self._Messageslist.options) - 1
                        self._screen.force_update()
                    try:
                        self._model._messageQueue.pop()
                    except IndexError:
                        pass
            else:
                self._usersSorted = sorted(self._builder.CurrentUsers, key=self._builder._status_order, reverse=True)
                self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(self._usersSorted)]
                self._screen.force_update()
            self._model._signal.clear()


    def reload(self):
        self._Forumslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(self._builder.CurrentUsers)]
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._header0.value = "Connected to: {} | User: {} | Currnet Chat: {}".format(self._builder._connectedTo, self._builder.CurrentUser, self._builder.CurrentChat)
        self.t1 = threading.Thread(target=self._chatFeeder)
        self.t1.daemon = True
        self.t1.start()

    @staticmethod
    def _exit():
        raise StopApplication('User requested to quit.')


def run(screen, scene):
    default = (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLACK)
    colorScheme = {
            'header': (Screen.COLOUR_WHITE, Screen.A_NORMAL, Screen.COLOUR_BLUE),
            'borders': default,
            'background': default,
            'label': default,
            'button': default,
            'focus_button': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'field': default,
            'focus_field': default,
            'edit_text': default,
            'title': default,
            'focus_edit_text': default,
            'selected_focus_field': (Screen.COLOUR_BLACK, Screen.A_NORMAL, Screen.COLOUR_WHITE),
            'scroll': default,
            'control': default,
            'disabled': default,
            'selected_control': default,
            'selected_focus_control': default,
            'focus_control': default,
            'invalid': default,
            'selected_field': default,
            'shadow': (0, None, 0)
        }
    logging.basicConfig(filename='ascii.log', level=logging.DEBUG)
    scenes = [
        Scene([myTest(screen, Builder, runtimeData, colorScheme)], -1, name="Main"),
        Scene([LoginView(screen, Builder, runtimeData, client, colorScheme)], -1, name="LoginForm"),
        Scene([TopicPanel(screen, Builder, runtimeData, colorScheme)], -1, name="TopicPanel"),
        Scene([NewTopic(screen, Builder, runtimeData, colorScheme)], -1, name="NewTopic")
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene)

def main():
    global runtimeData
    global client
    runtimeData = Model()
    client = Client
    last_scene = None
    while True:
        try:
            Screen.wrapper(run, arguments=[last_scene], catch_interrupt=True)
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

if __name__ == '__main__':
    main()


