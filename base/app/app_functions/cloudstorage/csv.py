import abc

from krules_core.base_functions import RuleFunctionBase

import csv
import io


class ProcessCSV_AsDict(RuleFunctionBase):

    def execute(self, driver, bucket, path, func, csvreader_kwargs={}):

        if type(driver) == abc.ABCMeta:
            driver = driver()
        container = driver.get_container(bucket)
        blob = container.get_blob(path)
        csv_in = io.BytesIO()
        driver.download_blob(blob, csv_in)
        csv_in.seek(0)
        with io.TextIOWrapper(csv_in, encoding="utf-8") as input_file:
            reader = csv.DictReader(input_file, **csvreader_kwargs)
            for drow in reader:
                func(drow, self)
