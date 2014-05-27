import os
import sys
import sublime
import sublime_plugin
import zlib
import base64
from threading import Thread

sys.path.append(os.path.join(os.path.dirname(__file__), 'third_party_libs'))

import socketIO_client
import diff_match_patch

# import logging
# logging.basicConfig(level=logging.DEBUG)


def get_buffer_contents(view):
    return view.substr(sublime.Region(0, view.size()))


class SeeMeCode(sublime_plugin.EventListener):
    def __init__(self):
        self.settings = sublime.load_settings('SeeMeCode.sublime-settings')
        self.settings.add_on_change('enabled', self.update_enabled)
        self.settings.add_on_change('server', self.reconnect)
        self.settings.add_on_change('port', self.reconnect)

        self.dmp = diff_match_patch.diff_match_patch()
        self.last_contents = None
        self.update_enabled()

    def update_enabled(self):
        self.enabled = self.settings.get('enabled')

    def ensure_started(self):
        if not hasattr(self, 'io'):
            self.reconnect()

    def reconnect(self):
        if self.enabled:
            print('SeeMeCode: Connecting to server')
            self.io = socketIO_client.SocketIO(self.settings.get('server'), self.settings.get('port'))
            # TODO this will create a thread every time!
            Thread(target=self.io.wait).start()

    def send_whole_file(self, view):
        if self.enabled:
            self.ensure_started()
            buffer_contents = get_buffer_contents(view)
            self.last_contents = buffer_contents
            contents_as_bytes = bytes(buffer_contents, 'utf-8')
            contents_compressed = zlib.compress(contents_as_bytes)
            contents_b64_encoded = base64.b64encode(contents_compressed)
            try:
                self.io.emit('file_contents', {'content': contents_b64_encoded.decode()})
            except socketIO_client.exceptions.SocketIOError:
                self.reconnect()

    def send_file_patches(self, view):
        if self.enabled:
            self.ensure_started()
            buffer_contents = get_buffer_contents(view)

            patches = self.dmp.patch_make(self.last_contents, buffer_contents)

            self.last_contents = buffer_contents
            try:
                self.io.emit('file_patches', {'patches': self.dmp.patch_toText(patches)})
            except socketIO_client.exceptions.SocketIOError:
                self.reconnect()

    def on_modified(self, view):
        if self.last_contents is not None:
            self.send_file_patches(view)
        else:
            self.send_whole_file(view)

    def on_activated(self, view):
        self.send_whole_file(view)
