# pipeline/reader.py

from llama_index.core import SimpleDirectoryReader


class Reader:

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        reader = SimpleDirectoryReader(input_files=[self.filename])
        documents = reader.load_data()
        return documents