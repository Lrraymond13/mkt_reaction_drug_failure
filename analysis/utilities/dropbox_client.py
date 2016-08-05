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
import pandas as pd


from analysis.dev import MIT_APP_ACCESS, LOCAL_PATH


class DropboxAPI(object):

    def __init__(self, access_key=None):
        self._access = access_key or MIT_APP_ACCESS
        self._client = dropbox.Dropbox(self._access)

    def _make_path(self, rel_path):
        curpath = os.path.abspath(os.curdir)
        return os.path.join(curpath, rel_path)

    def search(self, query, path=None):
        if not path:
            path = '/'
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

    def search_and_download(self, query, dropbox_path, local_path, serialize_delim=',', SEARCH_ONLINE=True):
        # file may be on local computer or dropbox
        # first search for file in dropbox file paths, if no results, search local
        # returns STRINGIO Object
        res = []
        ext = '.csv'
        if serialize_delim == 'p':
            ext = '.p'
        if SEARCH_ONLINE:
            res = self.search(query, dropbox_path)
        if SEARCH_ONLINE and len(res) > 0:
            print('Results found in dropbox, downloading {}'.format(res[0][0]))
            full_path = self.download(res[0][0])
        else:
            print('Searching local path')
            full_path = os.path.join(local_path, query + ext)
            print('Full path {}'.format(full_path))
        # if type is csv, use read csv, otherwise return pickle dump
        if serialize_delim == 'p':
            return pd.read_pickle(full_path)
        # otherwise, assume a csv
        return pd.read_csv(full_path, delimiter=serialize_delim)

    def upload_file(self, local_path, dropbox_path):
        # uploads a file to dropbox
        with open(local_path, 'r') as f:
            print('Uploading {local} to Dropbox as {path}'.format(
                local=local_path, path=dropbox_path))
            try:
                self._client.files_upload(f, dropbox_path, mode=WriteMode('overwrite'))
            except ApiError as err:
                # Not enough space error
                print err.error

    def _serialize_upload(self, dataset, local_path, dropbox_path, serialize_fmt, UPLOAD):
        # seializes dataset using format specified and uploads to dropbox
        # get attr on data set of fnc
        serialize_fnc = getattr(dataset, serialize_fmt)
        print('Serializing to local path {}'.format(local_path))
        serialize_fnc(local_path)
        if UPLOAD:
            self.upload_file(local_path, dropbox_path)

    def csv_upload_dataset(self, dataset, fname, csv_dir, dropbox_dir, UPLOAD=True):
        # writes file to csv and then from that csv to dropbox
        full_fname = os.path.join(csv_dir, fname)
        dropbox_fname = os.path.join(dropbox_dir, fname)
        self._serialize_upload(dataset, full_fname, dropbox_fname, 'to_csv', UPLOAD)

    def pickle_upload_dataset(self, dataset, fname, pickle_dir, dropbox_dir, UPLOAD=True):
        # writes file to csv and then from that csv to dropbox
        full_fname = os.path.join(pickle_dir, fname)
        dropbox_fname = os.path.join(dropbox_dir, fname)
        self._serialize_upload(dataset, full_fname, dropbox_fname, 'to_pickle', UPLOAD)





