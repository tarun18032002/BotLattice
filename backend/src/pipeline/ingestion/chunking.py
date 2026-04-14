from llama_index.core.node_parser import (
    SentenceSplitter,
    TokenTextSplitter,
    CodeSplitter,
    HTMLNodeParser,
    HierarchicalNodeParser,
    MarkdownNodeParser,
    SimpleNodeParser,
)


class Chunking:

    def __init__(self, chunking_request):
        """
        chunking_request : ChunkingRequest schema
        """
        self.config = chunking_request
        self.chunking_type = chunking_request.chunking_type.value

    def get_splitter(self):

        splitter_map = {

            "sentence": lambda: SentenceSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            ),

            "token": lambda: TokenTextSplitter(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            ),

            "code": lambda: CodeSplitter(
                language=self.config.language,
                chunk_lines=self.config.chunk_lines,
                chunk_lines_overlap=self.config.chunk_lines_overlap
            ),

            "html": lambda: HTMLNodeParser(),

            "markdown": lambda: MarkdownNodeParser(),

            "hierarchical": lambda: HierarchicalNodeParser.from_defaults(
                chunk_sizes=self.config.chunk_sizes
            ),

            "simple": lambda: SimpleNodeParser.from_defaults(
                chunk_size=self.config.chunk_size,
                chunk_overlap=self.config.chunk_overlap
            ),
        }

        if self.chunking_type not in splitter_map:
            raise ValueError(f"Invalid chunking type: {self.chunking_type}")

        return splitter_map[self.chunking_type]()

    def split(self, documents):
        try :
            splitter = self.get_splitter()

            nodes = splitter.get_nodes_from_documents(documents)

            return nodes
        except Exception as e:
            raise ValueError(f"Error during chunking: {str(e)}")