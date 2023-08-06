
asciiRyver
==========

asciiRyver is a `Ryver`_ chat client designed to be able to run in the terminal. This was built on the `Asciimatics`_ framework. This is not designed to be professional software, and it is still currently in beta. At present, there may be lots of bugs encountered, but the basic chat functionality is working, including: forums, workgroups, direct messaging, topics, and topic creation.

.. image:: Example.png

Requirements
------------
Python 3+

pip3

Installation
------------
Linux: `sudo pip3 install asciiRyver`

Windows: pip3 install asciiRyver

Usage
-----
Navigation:

 - TAB
 - Arrow keys

Commands:

 - ctrl-l = Login Menu
 - ctrl-t = Topic Menu
 - ctrl-c = Exit Application

User Status Legend:

 - '+' - Online
 - '-' - Inactive/Away
 - '(x)' - Do not disturb
 - '(username)' - Offline

once installed, you can start the chat with the command: asciiRyver

Forums and Workgroups will appear in the left column once logged in. You can select these rooms to switch to them.

Users for the current chat you are in will appear on the right column. Users are also selectable to being Direct Messaging.

Users are now sorted by status in the User column


Notes
-----
I will gladly take pull requests to help iron out issues! It has been a fun project to work on.

.. _Asciimatics: https://pypi.python.org/pypi/asciimatics
.. _Ryver: https://ryver.com/


TODO
----

 - clean up code


