from mangrove_surface.api import Api
import os.path as path
import posixpath
import requests
import sys
from requests_toolbelt.multipart.encoder import MultipartEncoder,\
    MultipartEncoderMonitor
from mangrove_surface.misc import ProgressBar


class Dataset(Api):

    resource = "datasets"

    @classmethod
    def get_all(cls, controller):
        return cls.request(controller, "get")

    @classmethod
    def create(cls, controller, name, *tags):
        return cls.request(
            controller, "post",
            data={
                "name": name,
                "tags": list(tags)
            }
        )

    @classmethod
    def generate_dictionary(cls, controller, id, separator):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, id),
            data={
                "separator": separator,
                "generate_dictionary": True
            }
        )

    @classmethod
    def retrieve_modalities(cls, controller, id, field):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, id),
            data={
                "modalities": field
            }
        )

    @classmethod
    def sort(cls, controller, id, keys=[]):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, id),
            data={
                "keys": keys
            }
        )

    @classmethod
    def complete_upload(cls, controller, id):
        return cls.request(
            controller, "patch", target=posixpath.join(cls.resource, id),
            data={"complete_upload": True}
        )

    @classmethod
    def patch_all(cls, controller, id, separator, field, keys=[]):
        return cls.request(
            controller, "patch",
            target=posixpath.join(cls.resource, id),
            data={
                "complete_upload": True,
                "separator": separator,
                "generate_dictionary": True,
                "modalities": field,
                "keys": keys
            }
        )

    @classmethod
    def signed_url(cls, controller, dataset_id, part_nb):
        return cls.request(
            controller, "get",
            target=posixpath.join(cls.resource, dataset_id, "part_url"),
            params={"signed_part": part_nb},

        )

    @classmethod
    def upload_chunk(cls, controller, signed_url, chunk, reset=3):
        r = requests.put(
            signed_url, data=chunk,
            headers={"Content-Length": repr(sys.getsizeof(chunk.encoder))}
        )
        if r.status_code != 200 and reset > 0:
            chunk.encoder.reset()
            cls.upload_chunk(controller, signed_url, chunk, reset=reset - 1)

    @classmethod
    def create_upload_patch_dataset(
        cls, controller, name, filepath, field=None, tags=[], keys=[],
        separator=",", chunksize=1073741824
    ):
        filepath, delete = fake_manager_file(filepath)
        dataset = cls.create(controller, name, *tags)
        with File(filepath, chunksize) as f:
            for i, chunk in enumerate(f):
                rep = cls.signed_url(controller, dataset.id(), i + 1)
                signed_url = rep.signed_url()
                cls.upload_chunk(controller, signed_url, chunk)
        # ## fake_manager_file ###
        if delete:
            os.remove(filepath)
        ##########################
        return cls.patch_all(
            controller, dataset.id(), separator, field, keys=keys
        )


import boto3
import tempfile
import os


def fake_manager_file(filepath):
    delete = False
    if isinstance(filepath, dict):
        if filepath["type"].lower() == "s3":
            delete = True
            filepathtmp = tempfile.mkstemp()[1]
            s3 = boto3.resource('s3')
            s3.Bucket(filepath["bucket"]).download_file(
                filepath["key"],
                filepathtmp
            )
        filepath = filepathtmp
    return filepath, delete


class File:

    class SubFile:

        def __init__(self, chunk):
            self.chunk = chunk
            self.len = len(chunk)
            self.i = 0

        def read(self, size):
            res = self.chunk[self.i:self.i + size]
            self.i += size
            return res

        def reset(self):
            self.i = 0

    def __init__(self, filepath, chunksize):
        self.filepath = filepath
        self.chunksize = chunksize
        self.prbar = ProgressBar(
            path.basename(filepath) + ': ',
            path.getsize(filepath)
        )

    def __enter__(self):
        self.file = open(self.filepath, "rb")
        return iter(self)

    def __iter__(self):
        i = 0
        for chunk in iter(lambda: self.file.read(self.chunksize), b""):
            f = self.SubFile(chunk)
            m = MultipartEncoderMonitor(
                f, lambda monitor: self.prbar.show(
                    i + monitor.bytes_read
                )
            )
            yield m
            i += f.len

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
