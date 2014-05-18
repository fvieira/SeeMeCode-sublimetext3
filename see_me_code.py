import os
import sys
import sublime
import sublime_plugin

sys.path.append(os.path.join(os.path.dirname(__file__), 'third_party_libs'))

import socketIO_client


def get_buffer_contents(view):
    return view.substr(sublime.Region(0, view.size()))


class SeeMeCode(sublime_plugin.EventListener):
    def ensure_started(self):
        if not hasattr(self, 'io'):
            print('SeeMeCode: Connecting to server')
            self.settings = sublime.load_settings('SeeMeCode.sublime-settings')
            self.settings.add_on_change('server', self.reconnect)
            self.settings.add_on_change('port', self.reconnect)
            self.reconnect()

    def reconnect(self):
        self.io = socketIO_client.SocketIO(self.settings.get('server'), self.settings.get('port'))

    def send_contents(self, view):
        self.ensure_started()
        buffer_contents = get_buffer_contents(view)
        try:
            self.io.emit('write', {'content': buffer_contents})
        except socketIO_client.exceptions.ConnectionError:
            self.reconnect()

    def on_modified(self, view):
        self.send_contents(view)

    def on_activated(self, view):
        self.send_contents(view)
