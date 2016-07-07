import dropbox
from dropbox.exceptions import ApiError, HttpError
from dropbox.files import WriteMode
import os
from os.path import basename, join, isfile
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


from analysis.dev import APP_ACCESS, LOCAL_PATH


class DropboxAPI(object):

    def __init__(self, access_key=None):
        self._access = access_key or APP_ACCESS
        self._client = dropbox.Dropbox(self._access)

    def _make_path(self, rel_path):
        curpath = os.path.abspath(os.curdir)
        return os.path.join(curpath, rel_path)

    def search(self, query, path=None):
        if not path:
            path = '/data'
        print('Searching {query} in path {path}'.format(query=query, path=path))
        r = self._client.files_search(path=path, query=query)
        return list((k.metadata.path_lower, k.metadata.size) for k in r.matches)

    def get_file(self, dropbox_path, local_path=None):
        base_name = basename(dropbox_path)
        if not local_path:
            local_path = join(LOCAL_PATH, base_name)
        file_exists = isfile(local_path)
        print('local path {}'.format(local_path))
        if not file_exists:
            with open(local_path, 'w') as f:
                os.utime(local_path, None)
        print('Saving to {}'.format(local_path))
        r = self._client.files_download_to_file(local_path, dropbox_path)
        return r

    def download(self, dropbox_path):
        print('downloading {}'.format(dropbox_path))
        try:
            meta, cont = self._client.files_download(dropbox_path)
        except HttpError as err:
            print('HTTP Connection Error {}'.format(str(err)))
            return None
        return StringIO(cont.content)

    def upload_file(self, local_path, dropbox_path=None):
        with open(local_path, 'r') as f:
            print('Uploading {local} to Dropbox as {path}'.format(
                local=local_path, path=dropbox_path))
            try:
                self._client.files_upload(f, dropbox_path, mode=WriteMode('overwrite'))
            except ApiError as err:
                # Not enough space error
                if (err.error.is_path() and
                        err.error.get_path().error.is_insufficient_space()):
                    sys.exit("ERROR: Cannot back up; insufficient space.")
                elif err.user_message_text:
                    print(err.user_message_text)
                    sys.exit()
                else:
                    print(err)
                    sys.exit()





