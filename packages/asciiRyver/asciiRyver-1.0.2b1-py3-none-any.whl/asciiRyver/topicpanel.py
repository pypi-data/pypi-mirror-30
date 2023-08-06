from asciimatics.widgets import Frame, Widget, Layout, Button, MultiColumnListBox, Divider
from asciimatics.exceptions import NextScene

class TopicPanel(Frame):
    """
    Display for the Topic Panel

    palette: Color scheme defined in __main__.py
    model: Model class defined in model.py used for passing data
    _builder: Framework class defined in framework.py for various functions

    Layout:
     _Channelslist: Left hand box displaying all Ryver channels
     _Topicslist: Right hand box displaying all Topics for the selected channel
     divideBox: Buffer created between Channel/Topic Boxes, and bottom Buttons
     buttonBox: Layout divided in half housing two buttons
    """
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
        _topicName = self._TopicsList.options[self._TopicsList.value][0][0]
        self._builder.CurrentChat = _topicName
        self._builder.CurrentMessages = []
        chatwidth = self.model._chatwidth
        self.model.running._topicChatHistory(chatwidth)
        raise NextScene("Main")

    def _retrieveTopics(self):
        _channel = self._Channelslist.options[self._Channelslist.value][0][0]
        self.model.running._topicListPuller(_channel)
        self.reload()


    def reload(self):
        self._Channelslist.options = [([x], i) for i, x in enumerate(self._builder._builtForum.keys())]
        self._TopicsList.options = [([x['title']], i) for i, x in enumerate(self._builder._builtTopics)]

