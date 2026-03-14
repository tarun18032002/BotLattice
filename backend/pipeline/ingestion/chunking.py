# pipeline/chunking.py

from llama_index.core.node_parser import (
    CodeSplitter,
    HierarchicalNodeParser,
    HTMLNodeParser,
    SentenceSplitter,
    SimpleNodeParser
)


class Chunking:

    def __init__(self, chunking_type="sentence", chunk_size=512, chunk_overlap=50):
        self.chunking_type = chunking_type
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def get_splitter(self):

        if self.chunking_type == "code":
            return CodeSplitter(language="python", chunk_lines=self.chunk_size)

        elif self.chunking_type == "hierarchical":
            return HierarchicalNodeParser.from_defaults(
                chunk_sizes=[self.chunk_size]
            )

        elif self.chunking_type == "html":
            return HTMLNodeParser()

        elif self.chunking_type == "sentence":
            return SentenceSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

        elif self.chunking_type == "simple":
            return SimpleNodeParser.from_defaults(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )

        else:
            raise ValueError("Invalid chunking type")

    def split(self, documents):

        splitter = self.get_splitter()

        nodes = splitter.get_nodes_from_documents(documents)

        return nodes