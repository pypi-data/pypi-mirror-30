import boto3
import os.path as path
import requests
import tempfile
from mangrove_surface.wrapper import Wrapper, should_be_terminated
from mangrove_surface.logger import logger, log_exception
from mangrove_surface.misc import iter_progress_bar
from mangrove_surface.api.feature_set import FeatureSet
from mangrove_surface.api.dataset import Dataset


class ExportWrapper(Wrapper):

    def _extra_init_(self):
        Wrapper._extra_init_(self)
        fs = FeatureSet.retrieve(
            self._controller, self.api_resource.feature_set_id()
        )
        self._main_dataset = Dataset.retrieve(
            self._controller,
            list(filter(lambda ds: ds['central'], fs.datasets()))[0]["id"]
        )

    def format(self):
        return self.api_resource.bin_format()

    @should_be_terminated
    def instances_submitted(self):
        """
        Number of instances submitted to export
        """
        return self._main_dataset.size()

    def classifier(self):
        """
        Return the classifier used
        """
        return self.accessor

    def binned_variables(self):
        """
        List the binned variables
        """
        return self.api_resource.binned_variables()

    def raw_variables(self):
        """
        List the raw variables
        """
        return self.api_resource.raw_variables()

    @should_be_terminated
    def download(self, filepath):
        """
        Download the export

        :param filepath: the filepath where store the classifier

        """
        from_url = self.api_resource.signed_url()

        logger.debug(
            'Download export : {from_path} > {to_path}'.
            format(from_path=from_url, to_path=filepath)
        )
        response = requests.get(
            from_url, stream=True
        )

        if not response.ok:
            log_exception(response.raise_for_status)()

        with open(filepath, 'wb') as handle:
            size = int(response.headers["content-length"])
            for block in iter_progress_bar(
                response.iter_content(1024),
                path.basename(filepath) + ': ',
                size, modulo=1024
            ):
                handle.write(block)

        logger.debug("Export downloaded")

    def push_s3(self, bucket, key):
        """
        Push the current export to S3

        :param bucket: the S3 bucket
        :param key: the S3 key
        """
        file = tempfile.mkstemp()[1]
        self.download(file)
        s3_client = boto3.client('s3')
        s3_client.upload_file(file, bucket, key)
