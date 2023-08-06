from asciimatics.widgets import TextBox, Text, Divider, Layout, MultiColumnListBox, Label, Widget, Frame, Button
from asciimatics.exceptions import NextScene, StopApplication, ResizeScreenError
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
import re
import threading
import time


class MainMenu(Frame):
    """
    Main Chat display for the program.

   palette: Color scheme defined in __main__.py
   _model: Model class defined in model.py for passing data
   _builder: Framework class defined in framework.py

   Layout:
       _header: Top banner housing connection, user, and current chat information
       _Forumslist: Left side column for all Ryver channels available
       _Messageslist: Center column for message display
       _Userslist: Right side column for users available in the current chat
       _footer: Bottom banner displaying shortcut commands
       sendBox: Box holding 'msg:|', user message, send button
    """

    def __init__(self, screen, builder, model, colors):
        super(MainMenu, self).__init__(screen,
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
        self._header = TextBox(1, as_string=True)
        self._header.disabled = True
        self._header.custom_colour = 'header'
        self._header.value = "Connected to: {} | User: {} | Current Chat: {}".format(self._builder._connectedTo,
                                                                                      self._builder.CurrentUser,
                                                                                      self._builder.CurrentChat)
        self.layout.add_widget(self._header, 0)

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
        self._chatCrt.value = 'msg|:'
        self._MsgBox = TextBox(1, name='userMsg')
        self.sendBox = Layout([6, 87, 7])
        self.add_layout(self.sendBox)
        self.sendBox.add_widget(self._chatCrt, 0)
        self.sendBox.add_widget(self._MsgBox, 1)
        self.sendBox.add_widget(Button('Send', on_click=self._sendMsg), 2)
        self.fix()
        self._model._chatwidth = self._Messageslist._get_width(0)


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
        return super(MainMenu, self).process_event(event)

    def _sendMsg(self):
        self.save()
        to = self._builder.CurrentChat
        # Check if we are in a topic
        if any(x['title'] == to for x in self._builder._builtTopics):
            _id = [x['id'] for x in self._builder._builtTopics if x['title'] == to]
            _id = _id[0]
            self._model.activeClient._send_topic(_id, self.data['userMsg'][0])
        # Check if we are in a forum/workgroup
        elif to in self._builder._builtForum.keys():
            _toJid = self._builder._builtForum[to][1]
            self._model.activeClient._on_send(_toJid, self.data['userMsg'][0])
        # Check if we are DM'ing
        elif any(x['username'] == to for x in self._builder._builtUsers):
            _toJid = [x['jid'] for x in self._builder._builtUsers if x['username'] == to]
            _toJid = _toJid[0]
            self._model.activeClient._on_send(_toJid, self.data['userMsg'][0])
        self._MsgBox.value = None
        self._MsgBox.focus()


    def _changeRoom(self):
        _newRoom = self._Forumslist.options[self._Forumslist.value][0][0]
        _textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeRoom(_newRoom, _textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        _usersSorted = sorted(self._builder.CurrentUsers, key=self._builder._status_order, reverse=True)
        self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(_usersSorted)]
        self._header.value = "Connected to: {} | User: {} | Currnet Chat: {}".format(self._builder._connectedTo,
                                                                                     self._builder.CurrentUser,
                                                                                     self._builder.CurrentChat)

    def _changeUser(self):
        _newUser = self._Userslist.options[self._Userslist.value][0][0]
        _newUser = re.sub(r'[^A-Za-z0-9\s]', '', _newUser)
        _textBoxWidth = self._Messageslist._get_width(0)
        self._model.running.changeDm(_newUser, _textBoxWidth)
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._header.value = "Connected to: {} | User: {} | Currnet Chat: {}".format(self._builder._connectedTo,
                                                                                     self._builder.CurrentUser,
                                                                                     self._builder.CurrentChat)

    def _chatFeeder(self):
        while True:
            time.sleep(0.1)
            self._model._signal.wait()
            if len(self._model._messageQueue) > 0:
                for i in self._model._messageQueue:
                    _textBoxWidth = self._Messageslist._get_width(0)
                    _sliced = self._model.running._chatSlicer(i, _textBoxWidth)
                    for i in _sliced:
                        _num = len(self._Messageslist.options)
                        self._Messageslist.options.append(([i], _num))
                        self._Messageslist.start_line = len(self._Messageslist.options)
                        self._Messageslist._line = len(self._Messageslist.options) - 1
                        self._screen.force_update()
                    try:
                        self._model._messageQueue.pop()
                    except IndexError:
                        pass
            else:
                _usersSorted = sorted(self._builder.CurrentUsers, key=self._builder._status_order, reverse=True)
                self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(_usersSorted)]
                self._screen.force_update()
            self._model._signal.clear()


    def reload(self):
        self._Forumslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._Userslist.options = [([x['usernameStatus']], i) for i, x in enumerate(self._builder.CurrentUsers)]
        self._Messageslist.options = [([x], i) for i, x in enumerate(self._builder.CurrentMessages)]
        self._header.value = "Connected to: {} | User: {} | Currnet Chat: {}".format(self._builder._connectedTo,
                                                                                     self._builder.CurrentUser,
                                                                                     self._builder.CurrentChat)
        self.t1 = threading.Thread(target=self._chatFeeder)
        self.t1.daemon = True
        self.t1.start()

    @staticmethod
    def _exit():
        raise StopApplication('User requested to quit.')

