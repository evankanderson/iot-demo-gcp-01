import abc
from io import BytesIO

from krules_core.base_functions import RuleFunctionBase


class GetBlobIO(RuleFunctionBase):

    def execute(self, driver, bucket, path, payload_dest="cloudstorage_blob"):
        if type(driver) == abc.ABCMeta:
            driver = driver()
        container = driver.get_container(bucket)
        blob = container.get_blob(path)
        dest = BytesIO()
        driver.download_blob(blob, dest)
        dest.seek(0)
        self.payload[payload_dest] = dest


class DeleteBlob(RuleFunctionBase):

    def execute(self, driver, bucket, path):
        if type(driver) == abc.ABCMeta:
            driver = driver()
        container = driver.get_container(bucket)
        blob = container.get_blob(path)
        driver.delete_blob(blob)



