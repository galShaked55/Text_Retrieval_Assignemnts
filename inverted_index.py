# This module will implement the InvertedIndex design and population.
from collections import defaultdict
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
    def __init__(self, data_path_str, output_path_str='./out/Part_2.txt'):
        """
        Creates a new empty inverted index based on the input data_path
        :param data_path_str: String representing the input data directory path, if not a directory, creation will fail.
        """
        self.term_docs_dict = defaultdict(PostingList) # The data structure to populate as the inverted index.\


        data_p = Path(data_path_str)
        if not data_p.exists():
            print(f"ERROR: Couldn't init the inverted index since the input data directory path passed was not found")
            raise FileNotFoundError(f"The specified path does not exist: '{data_path_str}'")
        if not data_p.is_dir():
            print(f"ERROR: Couldn't init the inverted index since the input data directory path passed is not a directory")
            raise NotADirectoryError(f"Path exists, but is not a directory: '{data_path_str}'")

        self.data_p_obj = data_p
        self.file_counter = 0

    def populate(self, verbose=False):
        """
        This method iterates recursively each file in this InvertedIndex instance's self.data_p_obj.
        It parses only directories with name that starts with 'AP'. Then each file is processed to populate the inverted index dictionary.
        """
        for entry in self.data_p_obj.rglob('AP*'):
            if entry.is_file():
                if verbose and self.file_counter % 100 == 0:
                    print(f"INFO: Processing now: {entry}")
                self.file_counter += 1
                self.process_file(entry)

    def process_file(self, entry):
        """
        This method opens the given Path object file and reads it line by line.
        It handles the creation of new docs and calls methods to add new terms and docs to the inverted index.
        :param entry: a Path object representing the file to process
        """
        try:
            with open(entry, 'r') as f:
                in_doc = False
                in_text = False
                new_doc = None

                for line in f:
                    line = line.strip()

                    # Check for document start
                    if line.startswith(self.START_DOC_TAG):
                        in_doc = True
                        new_doc = None
                        continue

                    # Check for document number
                    if in_doc and self.START_DOCNO_TAG in line:
                        new_doc = Document(self.extract_doc_name(line))
                        continue

                    # Check for text start
                    if in_doc and line.startswith(self.START_TEXT_TAG):
                        in_text = True
                        continue

                    # Check for text end
                    if in_text and self.END_TEXT_TAG in line:
                        in_text = False
                        continue

                    # Process text content immediately
                    if in_text:
                        self.process_text_line(line, new_doc)
                        continue

                    # Check for document end
                    if line.startswith(self.END_DOC_TAG):
                        in_doc = False
                        new_doc = None
                        continue
        except OSError as e:
            print(f"Couldn't parse file: {entry}. This OS error occurred: {e}")
        except Exception as e:
            print(f"Couldn't parse file: {entry}. This unexpected error occurred: {e}")

    def process_text_line(self, text_line, document):
        """
        This method gets a line of text within a document and parses it.
        For each word:
            If the word already exist in the index:
                if the document is not already in the word's postings list, append it.
                o/w continue
            O/w:
                Add the word as new term in the index and append the current document.
        """
        words = text_line.split()

        for word in words:
            if word:
                posting_list = self.term_docs_dict[word]
                last_doc = posting_list.get_last_doc()

                if last_doc != document:
                    posting_list.append(document)


    def extract_doc_name(self, line):
        # Find the position after the first tag
        start = line.find('>') + 1

        # Find the position of the first '<' after that
        end = line.find('<', start)

        return line[start:end].strip()

    def print_index(self):
        for term, postings_list in self.term_docs_dict.items():
            print(f"term: {term}")
            print(f"Postings List: {postings_list}")
            print()


class PostingList(list):
    """
    A list for storing Documents (postings) with an automatically
    updated 'size' property.
    """
    def __init__(self, *args):
        super().__init__(*args)
        # The size property tracks the number of documents (postings)
        self.freq = len(self)

    # Override the append method to update the size property
    def append(self, item):
        super().append(item)
        self.freq += 1

    def __repr__(self):
        # Shows both the size and the contents for debugging
        return f"PostingList(size={self.freq}, docs={super().__repr__()})"

    def get_last_doc(self):
        if self.freq > 0:
            return self[-1]
        else:
            return None

class Document:
    """
    Document instances represent a single document in the proivided colleciton.
    Each document has two identifiers - the document name (as extracted from its raw <DOCNO> element) and the document id.
    The document id is an incremental integer given to the documents according to their order of initialization (i.e, the point int time they were processed).
    """
    # global variable for incremented id init with 0
    ID = 0

    def __init__(self, raw_id):
        self.doc_id = raw_id
        self.doc_idx = Document.ID
        Document.ID += 1

    def __eq__(self, other):
        if isinstance(other, Document):
            return self.doc_idx == other.doc_idx
        return NotImplemented

    def __repr__(self):
        # Shows both the size and the contents for debugging
        return f"Document(doc_id={self.doc_id}, doc_idx={self.doc_idx})"


def test_inverted_index_basic():
    """Test basic InvertedIndex functionality with sample documents."""
    print("="*60)
    print("TESTING INVERTED INDEX - BASIC FUNCTIONALITY")
    print("="*60)

    # Test Document class
    print("\nTEST 1: Document Creation")
    print("-"*60)
    Document.ID = 0  # Reset counter for testing
    doc1 = Document("AP890101-0001")
    doc2 = Document("AP890101-0002")
    doc3 = Document("AP890101-0003")

    print(f"doc1: {doc1}")
    print(f"doc2: {doc2}")
    print(f"doc3: {doc3}")
    print(f"Total documents created: {Document.ID}")

    # Test PostingList class
    print("\nTEST 2: PostingList Creation and Append")
    print("-"*60)
    posting_list = PostingList()
    print(f"Empty posting list: {posting_list}")
    print(f"freq: {posting_list.freq}")

    posting_list.append(doc1)
    posting_list.append(doc2)
    posting_list.append(doc3)
    print(f"\nAfter adding 3 documents: {posting_list}")
    print(f"freq: {posting_list.freq}")
    print(f"get_last_doc(): {posting_list.get_last_doc()}")

    # Test basic inverted index structure
    print("\nTEST 3: Basic Inverted Index Structure")
    print("-"*60)
    term_docs_dict = defaultdict(PostingList)

    # Simulate adding terms
    term_docs_dict['cat'].append(doc1)
    term_docs_dict['cat'].append(doc2)
    term_docs_dict['dog'].append(doc2)
    term_docs_dict['dog'].append(doc3)
    term_docs_dict['mouse'].append(doc1)

    print(f"Index contains {len(term_docs_dict)} terms")
    for term, postings in term_docs_dict.items():
        doc_ids = [doc.doc_id for doc in postings]
        print(f"  '{term}' (freq={postings.freq}): {doc_ids}")

    print("\n" + "="*60)
    print("BASIC TESTS COMPLETED!")
    print("="*60 + "\n")


def test_inverted_index_on_data(data_path, max_files=None):
    """Test InvertedIndex on actual data with optional file limit."""
    print("="*60)
    print("TESTING INVERTED INDEX - ON DATA")
    print("="*60)
    print(f"Data path: {data_path}")

    # Reset document counter
    Document.ID = 0

    print("\nCreating inverted index...")
    ii = InvertedIndex(data_path)

    if max_files:
        print(f"Processing first {max_files} files only...", flush=True)
        # Temporarily store the original rglob method
        file_count = 0
        for entry in ii.data_p_obj.rglob('AP*'):
            if entry.is_file():
                if file_count >= max_files:
                    break
                ii.process_file(entry)
                file_count += 1
                if file_count % 50 == 0:
                    print(f"  Processed {file_count} files...", flush=True)
    else:
        print("Processing all files...")
        ii.populate(verbose=True)

    # Print statistics
    print(f"\n{'='*60}")
    print("STATISTICS")
    print(f"{'='*60}")
    print(f"Total documents processed: {Document.ID}")
    print(f"Total unique terms: {len(ii.term_docs_dict)}")

    # Show sample terms
    print(f"\nSample terms (first 10):")
    for i, (term, postings) in enumerate(list(ii.term_docs_dict.items())[:10]):
        doc_ids = [doc.doc_id for doc in postings[:3]]  # Show first 3 docs
        more = f" ... +{postings.freq - 3} more" if postings.freq > 3 else ""
        print(f"  '{term}' (freq={postings.freq}): {doc_ids}{more}")

    # Find some common terms
    print(f"\nLooking for common terms:")
    common_terms = ['the', 'a', 'an', 'of', 'in', 'to', 'and', 'is', 'was', 'for']
    for term in common_terms:
        if term in ii.term_docs_dict:
            freq = ii.term_docs_dict[term].freq
            print(f"  '{term}': found in {freq} documents")

    print("\n" + "="*60)
    print("DATA TESTS COMPLETED!")
    print("="*60 + "\n")

    return ii


if __name__ == '__main__':
    import sys

    # Check if user wants to run tests
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        # Run basic tests first
        test_inverted_index_basic()

        # Ask user if they want to test on actual data
        print("Do you want to test on actual data? (y/n)")
        # For automation, check if there's a 3rd argument
        if len(sys.argv) > 2:
            data_path = sys.argv[2]
            max_files = int(sys.argv[3]) if len(sys.argv) > 3 else None
            test_inverted_index_on_data(data_path, max_files)

        sys.exit(0)


'''# Tests:
    ## Small test:
    data_path = 'C:/Users/User/TextRetreival/Assignment1/small_test_data'
    #small_test_ii = InvertedIndex(data_path)
    #small_test_ii.populate(verbose=True)
    # print(f"Inverted index:")
    #small_test_ii.print_index()
    # print(f"Documents counter = {Document.ID}")

    ## Large test:
    # data_path = 'C:/Users/User/TextRetreival/Assignment1/test_data'
    # test_ii = InvertedIndex(data_path)
    # test_ii.populate(verbose=True)
    # print(f"Inverted index:")
    # test_ii.print_index()
    # print(f"Documents counter = {Document.ID}")
    # print(f"Correct # of docs = 297")

    # Example of usage:
    data_path = 'C:/Users/eynavoz/Documents/courses/ms_first_year/text_retreival/Text_Retrieval_Assignemnts/data/AP_Coll_Parsed_1'
    ii = InvertedIndex(data_path) # Create a new empty Inverted Index which will be based on the data_path collection
    ii.populate(verbose=True) # populate the inverted index | verbose true if you want printings about the pace of progress
    print(f"Documents counter = {Document.ID}")
'''



