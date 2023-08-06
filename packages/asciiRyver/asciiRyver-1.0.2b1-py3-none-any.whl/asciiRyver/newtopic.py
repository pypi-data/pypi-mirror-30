from asciimatics.widgets import Frame, Layout, Button, Text
from asciimatics.exceptions import NextScene

class NewTopic(Frame):
    """
    Display for creating a new topic

    palette: Color scheme defined in __main__.py
    model: Model class for passing data, defined in model.py
    _builder: Framework class for function calls, in framework.py

    Layout:
        layout: Basic center display with 3 fields to be filled out
        button_bar: Housing the 'OK' and 'Cancel' Buttons
    """
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
        _topicCreate = self.model.running._createTopic(self.data['channel'],
                                                            self.data['subject'],
                                                            self.data['body'])
        try:
            if _topicCreate.status_code == 201:
                raise NextScene("TopicPanel")
            else:
                self._scene.add_effect(PopUpDialog(self.screen, "Topic Creation Failed! HTTP Code: "+str(_topicCreate.status_code),"X",on_close=None))
        except AttributeError:
            self._scene.add_effect(PopUpDialog(self.screen, "Topic Creation Failed! NOTE: Channel field is case sensitive!", "X", on_close=None))

    def _cancel(self):
        raise NextScene('TopicPanel')
