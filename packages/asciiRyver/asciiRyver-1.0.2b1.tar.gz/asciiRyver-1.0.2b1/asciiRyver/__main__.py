from asciiRyver.mainmenu import MainMenu
from asciiRyver.newtopic import NewTopic
from asciiRyver.topicpanel import TopicPanel
from asciiRyver.loginview import LoginView
from asciiRyver.model import Model
from asciiRyver.framework import Builder
from asciiRyver.client import Client
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.scene import Scene
from asciimatics.exceptions import ResizeScreenError
import sys



def run(screen, scene):
    """
    Function that builds the screen for asciimatics

    colorScheme: Dict with color values (FG, Font-Style, BG)
    scenes: list of Scene objects that the program will render
    """
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
    scenes = [
        Scene([MainMenu(screen, Builder, runtimeData, colorScheme)], -1, name="Main"),
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


