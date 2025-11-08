# This module will implement the InvertedIndex design and population.
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
    pass

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
    pass
