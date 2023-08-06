from asciimatics.widgets import Frame, Layout, Button, PopUpDialog, Text
from asciimatics.exceptions import NextScene
import requests

class LoginView(Frame):
    """
    Display for the Login Menu to connect to Ryver

    palette: Color scheme defined in __main__.py
    model: Model class defined in model.py for passing data
    _builder: Framework class defined in framework.py
    _client: Websocket client from client.py
    """

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
        try:
            loginRequest = requests.post('https://'+self.data['organization']+'.ryver.com/api/1/odata.svc/User.Login()',
                                            auth=(self.data['email'], self.data['password']))
            if loginRequest.status_code == 200:
                # Success
                response = loginRequest.json()
                payload = {'email': self.data['email'], 'password': self.data['password'],
                        'org': self.data['organization'], 'data': response}
                self._builder(payload)
                self.model.running = self._builder(payload)
                newClient = self._client(payload, self.model)
                newClient.run(payload)
                self.model.activeClient = newClient
                raise NextScene("Main")
            else:
                self._scene.add_effect(PopUpDialog(self.screen, "Login Failed!", "X", on_close=None))
        except UnicodeError:
            self._scene.add_effect(PopUpDialog(self.screen, "Please fill out all fields!", "X", on_close=None))

    def _cancel(self):
        raise NextScene("Main")

