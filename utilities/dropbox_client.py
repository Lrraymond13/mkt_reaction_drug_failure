import dropbox

from dev import APP_ACCESS, DATA_ROOT


class DropboxWrapper(object):

    def __init__(self):
        self.client = dropbox.client.DropboxClient(APP_ACCESS)
        self.file_root = DATA_ROOT

    def get_file(self, filename, root=None):
        if not root:
            root = self.file_root
        rt_filename = root + filename
        return self.client.get_file_and_metadata(rt_filename)

    def push_file(self, filename, root=None):
        if not root:
            root = self.file_root
        rt_filename = root + filename
        response = self.client.put_file(rt_filename, 'f')
        return response




