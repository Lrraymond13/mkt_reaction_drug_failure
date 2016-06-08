import dropbox
from os.path import join

from dev import APP_ACCESS, DATA_ROOT


class DropboxWrapper(object):

    def __init__(self):
        self.client = dropbox.client.DropboxClient(APP_ACCESS)
        self.file_root = DATA_ROOT

    def _make_filename(self, path, root):
        if not root:
            root = self.file_root
        return join(root, path)

    def get_file(self, filename, root=None):
        rt_filename = self._make_filename(filename, root)
        print('Accessing {}'.format(rt_filename))
        f, meta = self.client.get_file_and_metadata(rt_filename)
        return f

    def push_file(self, filename, root=None):
        rt_filename = self._make_filename(filename, root)
        response = self.client.put_file(rt_filename, 'f')
        return response




