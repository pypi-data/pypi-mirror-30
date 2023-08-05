from pathlib import Path
import os
import requests
from urllib.parse import urlparse
import xyxy.config
from tqdm import tqdm
import abc
import csv
import shutil
import inspect


class Formula(abc.ABC):

    def __init__(self):
        self.name = self.__class__.__name__.lower()
        self.formula_dir = Path(xyxy.config.xyxy_home_dir).expanduser() / self.name
        self.base_dir = self.formula_dir / 'data'

        self.title = None
        self.description = None
        self.homepage = None

        self.files = None
        self.parts = None

    def get_file_destination(self, file):
        if file.get('as') is None:
            o = urlparse(file.get('url'))
            return self.base_dir / os.path.basename(o.path)
        else:
            return self.base_dir / file.get('as')

    def download_file(self, file):
        destination = self.get_file_destination(file)

        chunk_size = 1024

        r = requests.get(file.get('url'), stream=True)

        r.raise_for_status()

        total_size = int(r.headers.get('content-length', 0))

        with open(destination, 'wb') as f:
            for chunk in tqdm(r.iter_content(chunk_size), total=total_size // chunk_size + 1,
                              unit='KB', leave=True):
                if chunk:
                    f.write(chunk)

        return destination

    def download(self):
        os.makedirs(self.base_dir, exist_ok=True)

        for file in self.files:
            self.download_file(file)
        self.post_download()

    @property
    def is_multipart(self):
        return self.parts is not None

    def post_download(self):
        pass

    def is_downloaded(self):
        if self.files is None:
            return os.listdir(self.base_dir) != []
        else:
            return all([os.path.isfile(self.get_file_destination(file)) for file in self.files])

    def clear(self):
        shutil.rmtree(self.formula_dir)

    def clear_data(self):
        shutil.rmtree(self.base_dir)

    @abc.abstractmethod
    def validate(self):
        pass

    @abc.abstractmethod
    def load(self):
        pass


def validate_formula(formula):
    formula.clear_data()
    formula.download()

    assert formula.is_downloaded()
    formula.validate()

    assert formula.title is not None
    assert formula.description is not None
    assert formula.homepage is not None

    parameters = inspect.signature(formula.load).parameters

    if formula.parts is not None or len(parameters) > 0:
        assert formula.parts is not None
        assert len(parameters) == 1
        for key in formula.parts.keys():
            assert formula.load(key) is not None
    else:
        assert formula.parts is None
        assert len(parameters) == 0
        assert formula.load() is not None
