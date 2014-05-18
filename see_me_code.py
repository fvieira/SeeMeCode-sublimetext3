import os
import sys
import sublime
import sublime_plugin

sys.path.append(os.path.join(os.path.dirname(__file__), 'third_party_libs'))

from socketIO_client import SocketIO


def get_buffer_contents(view):
    return view.substr(sublime.Region(0, view.size()))


class SeeMeCode(sublime_plugin.EventListener):
    def ensure_started(self):
        if not hasattr(self, 'io'):
            print('SeeMeCode: Connecting to server')
            settings = sublime.load_settings('SeeMeCode.sublime-settings')
            self.io = SocketIO(settings.get('server'), settings.get('port'))

    def on_modified(self, view):
        self.ensure_started()
        # for pos in view.sel():
        #     print(view.line(pos))

        buffer_contents = get_buffer_contents(view)
        self.io.emit('write', {'content': buffer_contents})

    def on_activated(self, view):
        self.ensure_started()
        buffer_contents = get_buffer_contents(view)
        self.io.emit('write', {'content': buffer_contents})
