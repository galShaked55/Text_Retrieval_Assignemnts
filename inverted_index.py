# This module will implement the InvertedIndex design and population.
from collections import defaultdict
from logging import exception
from pathlib import Path

class InvertedIndex:
    """
    Idea:
    init dict of {term: list_of docs}
    For each document:
        for each TEXT tag:
            for each word:
                if word not in dict:
                    create new entry in the dict with the word as a key.
                    init a new list of docs for this new term and append the current document (incrementalDocId, original_name)

    """
    # Constants defintions
    START_TEXT_TAG = "<TEXT>"
    END_TEXT_TAG = "</TEXT>"
    START_DOC_TAG = "<DOC>"
    END_DOC_TAG = "</DOC>"
    START_DOCNO_TAG = "<DOCNO>"
    END_DOCNO_TAG = "</DOCNO>"

    def __init__(self, data_path_str, output_path_str='./out/Part_2.txt'):
        """
        Creates a new empty inverted index based on the input data_path
        :param data_path: String representing the input data directory path, if not a directory, creation will fail.
        :param output_path: String representing the output path to write the results text file into.
        If not provided, './out/Part_2.txt' will be the output file location.
        """
        self.term_docs_dict = defaultdict(list) # The data structure to populate as the inverted index.\
        self.output_p_obj = Path(output_path_str)

        data_p = Path(data_path_str)
        if not data_p.exists():
            print(f"ERROR: Couldn't init the inverted index since the input data directory path passed was not found")
            raise FileNotFoundError(f"The specified path does not exist: '{data_path_str}'")
        if not data_p.is_dir():
            print(f"ERROR: Couldn't init the inverted index since the input data directory path passed is not a directory")
            raise NotADirectoryError(f"Path exists, but is not a directory: '{data_path_str}'")

        self.data_p_obj = data_p




    def populate(self, verbose=False):
        """
        This method iterates recursively each file in this InvertedIndex instance's self.data_p_obj.
        It parses only directories with name that starts with 'AP'. Then each file is processed to populate the inverted index dictionary.
        """
        for entry in self.data_p_obj.rglob('AP*'):
            if entry.is_file():
                self.process_file(entry)

    def process_file(self, entry):



class Term:
    """
    english word + its frequency
    * term's frequency should be maintained while building the index with counter.
    """
    pass

class Document:
    """
    Incremental DocId + original doc identifier.
    """
    # global variable for incremented id init with 0
    """
    def __init__(self, original_id):
        self.doc_id = original_id
        self.doc_idx = variable
        variable += 1
    """

if __name__ == '__main__':
    data_path = 'C:/Users/User/TextRetreival/Assignment1/data-20251108'
    example = InvertedIndex(data_path)
    example.populate()

