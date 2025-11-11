# This module will implement the boolean retrieval logic.
class BooleanRetrieval:
    """
    A class for evaluating boolean queries in Reverse Polish Notation (RPN) against an inverted index.
    Methods:
        evaluate(inverted_index):
            Evaluates a boolean query using a stack-based RPN algorithm.
            Reference: https://mathworld.wolfram.com/ReversePolishNotation.html
            Supports operators: AND, OR, NOT

        and_query(term_1_list, term_2_list):
            Performs intersection of two sorted posting lists (AND operation).
            Returns documents that appear in both lists.
            Uses the merge algorithm from lecture with two-pointer technique
        or_query(term_1_list, term_2_list):
            Performs union of two sorted posting lists (OR operation).
            Returns documents that appear in either list, without duplicates.
            Uses merge algorithm to combine lists efficiently.

        and_not_query(term_1_list, term_2_list):
            Performs set difference of two sorted posting lists (AND-NOT operation).
            Returns documents in term_1_list that are NOT in term_2_list.
            Uses merge algorithm to exclude matching documents.

    """

    def __init__(self, boolean_query):
        self.booleanquery = boolean_query


    def evaluate(self, inverted_index):
        """
        Retrieve a set of matching documents given an inverted index and a Boolean query in RPN.

        In practice RPN can be conveniently evaluated using a stack structure.
        Reading the expression from left to right, the following operations are performed:
            1. If a value appears next in the expression, push this value on to the stack.
            2. If an operator appears next, pop two items from the top of the stack and
               push the result of the operation on to the stack.

        Args:
            inverted_index: Dictionary mapping terms to posting lists (sorted by doc_idx)

        Returns:
            List of document objects that match the boolean query
        """
        stack = []
        operators = {'AND', 'OR', 'NOT'}

        # Split the query into tokens
        tokens = self.booleanquery.split()

        for token in tokens:
            if token in operators:
                # Pop two operands from the stack
                if len(stack) < 2:
                    raise ValueError(f"Invalid query: not enough operands for operator {token}")

                operand2 = stack.pop()
                operand1 = stack.pop()

                # Apply the operation
                if token == 'AND':
                    # Optimization: pass shorter list first to minimize comparisons
                    size1 = self._get_list_size(operand1)
                    size2 = self._get_list_size(operand2)

                    if size2 < size1:
                        result = self.and_query(operand2, operand1)
                    else:
                        result = self.and_query(operand1, operand2)
                elif token == 'OR':
                    result = self.or_query(operand1, operand2)
                elif token == 'NOT':
                    result = self.and_not_query(operand1, operand2)

                # Push result back onto stack
                stack.append(result)
            else:
                # It's a term - get its posting list
                posting_list = inverted_index.get(token, [])
                stack.append(posting_list)

        # After processing all tokens, the stack should contain exactly one element
        if len(stack) != 1:
            raise ValueError("Invalid query: stack does not contain exactly one result")

        return stack[0]

    def _get_list_size(self, lst):
        """
        Get the size of a list, using freq field if available (PostingList),
        otherwise using len() for regular lists.

        Args:
            lst: A PostingList or regular list

        Returns:
            int: The size of the list
        """
        if hasattr(lst, 'freq'):
            return lst.freq
        return len(lst)

    def and_query(self, term_1_list, term_2_list):
        """Find intersection of two sorted lists of document objects.

        Args:
            term_1_list: List of document objects sorted by doc_idx
            term_2_list: List of document objects sorted by doc_idx

        Returns:
            List of document objects that appear in both lists, sorted by doc_idx"""
        result_list = []
        p1 = 0
        p2 = 0

        # Get sizes once to avoid repeated function calls
        size1 = self._get_list_size(term_1_list)
        size2 = self._get_list_size(term_2_list)

        while p1 < size1 and p2 < size2:
            #Adding only the elments that are in both lists
            if term_1_list[p1].doc_idx == term_2_list[p2].doc_idx:
                result_list.append(term_1_list[p1])
                p1 += 1
                p2 += 1
            # If the elemnt isnt in one of the lists proceed
            elif term_1_list[p1].doc_idx < term_2_list[p2].doc_idx:
                p1+=1
            else:
                p2+=1
        return result_list
    
    def or_query(self, term_1_list, term_2_list):
        """Create union of two sorted lists of document objects.

        Args:
            term_1_list: List of document objects sorted by doc_idx
            term_2_list: List of document objects sorted by doc_idx

        Returns:
            List of document objects that appear in one of the lists, sorted by doc_idx"""
        result_list = []
        p1 = 0
        p2 = 0

        # Get sizes once to avoid repeated function calls
        size1 = self._get_list_size(term_1_list)
        size2 = self._get_list_size(term_2_list)

        # Merge while both lists have elements
        while p1 < size1 and p2 < size2:
            if term_1_list[p1].doc_idx < term_2_list[p2].doc_idx:
                result_list.append(term_1_list[p1])
                p1 += 1
            elif term_1_list[p1].doc_idx > term_2_list[p2].doc_idx:
                result_list.append(term_2_list[p2])
                p2 += 1
            else:  # Equal: add once, advance both
                result_list.append(term_1_list[p1])
                p1 += 1
                p2 += 1

        # Add remaining elements from whichever list that still have elements
        while p1 < size1:
            result_list.append(term_1_list[p1])
            p1 += 1

        while p2 < size2:
            result_list.append(term_2_list[p2])
            p2 += 1

        return result_list
         
    def and_not_query(self, term_1_list, term_2_list):
        """Return all elements in term_1_list that are NOT in term_2_list.

        Args:
            term_1_list: List of document objects sorted by doc_idx
            term_2_list: List of document objects sorted by doc_idx

        Returns:
            List of documents in term_1_list but not in term_2_list, sorted by doc_idx
        """
        result_list = []
        p1 = 0
        p2 = 0

        # Get sizes once to avoid repeated function calls
        size1 = self._get_list_size(term_1_list)
        size2 = self._get_list_size(term_2_list)

        # Process while both lists have elements
        while p1 < size1 and p2 < size2:
            if term_1_list[p1].doc_idx < term_2_list[p2].doc_idx:
                # Element in term_1 but not in term_2 - add it
                result_list.append(term_1_list[p1])
                p1 += 1
            elif term_1_list[p1].doc_idx == term_2_list[p2].doc_idx:
                # Element in both - skip it (don't add)
                p1 += 1
                p2 += 1
            else:  # term_1_list[p1].doc_idx > term_2_list[p2].doc_idx
                # term_2 element is smaller, advance p2
                p2 += 1

        # Add all remaining elements from term_1_list
        # (if we got to the end of term_2_list, these are definitely not in term_2)
        while p1 < size1:
            result_list.append(term_1_list[p1])
            p1 += 1

        return result_list


def test_query_functions():
    """Test the query functions with sample posting lists."""
    from inverted_index import Document, PostingList

    print("="*60)
    print("TESTING QUERY FUNCTIONS")
    print("="*60)

    # Create sample documents
    doc1 = Document("AP-001")
    doc2 = Document("AP-002")
    doc3 = Document("AP-003")
    doc4 = Document("AP-004")
    doc5 = Document("AP-005")

    # Create posting lists
    list_a = PostingList([doc1, doc2, doc3, doc5])  # docs: 0, 1, 2, 4
    list_b = PostingList([doc2, doc3, doc4])         # docs: 1, 2, 3
    list_c = PostingList([doc1, doc4, doc5])         # docs: 0, 3, 4

    print(f"\nTest Data:")
    print(f"list_a (freq={list_a.freq}): {[doc.doc_id for doc in list_a]}")
    print(f"list_b (freq={list_b.freq}): {[doc.doc_id for doc in list_b]}")
    print(f"list_c (freq={list_c.freq}): {[doc.doc_id for doc in list_c]}")

    br = BooleanRetrieval("")  # Create instance for testing

    # Test AND query
    print(f"\n{'='*60}")
    print("TEST 1: AND Query (Intersection)")
    print(f"{'='*60}")
    print("list_a AND list_b (expected: AP-002, AP-003)")
    result = br.and_query(list_a, list_b)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    print("\nlist_a AND list_c (expected: AP-001, AP-005)")
    result = br.and_query(list_a, list_c)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    print("\nlist_b AND list_c (expected: AP-004)")
    result = br.and_query(list_b, list_c)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    # Test OR query
    print(f"\n{'='*60}")
    print("TEST 2: OR Query (Union)")
    print(f"{'='*60}")
    print("list_a OR list_b (expected: AP-001, AP-002, AP-003, AP-004, AP-005)")
    result = br.or_query(list_a, list_b)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    print("\nlist_b OR list_c (expected: AP-001, AP-002, AP-003, AP-004, AP-005)")
    result = br.or_query(list_b, list_c)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    # Test AND-NOT query
    print(f"\n{'='*60}")
    print("TEST 3: AND-NOT Query (Set Difference)")
    print(f"{'='*60}")
    print("list_a AND-NOT list_b (expected: AP-001, AP-005)")
    result = br.and_not_query(list_a, list_b)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    print("\nlist_b AND-NOT list_c (expected: AP-002, AP-003)")
    result = br.and_not_query(list_b, list_c)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    print("\nlist_c AND-NOT list_a (expected: AP-004)")
    result = br.and_not_query(list_c, list_a)
    print(f"Result: {[doc.doc_id for doc in result]}")
    print(f"Result size: {len(result)}")

    # Test with evaluate function
    print(f"\n{'='*60}")
    print("TEST 4: RPN Query Evaluation")
    print(f"{'='*60}")

    # Create a simple inverted index
    inverted_index = {
        'cat': list_a,
        'dog': list_b,
        'mouse': list_c
    }

    print("\nInverted Index:")
    print(f"  'cat': {[doc.doc_id for doc in inverted_index['cat']]}")
    print(f"  'dog': {[doc.doc_id for doc in inverted_index['dog']]}")
    print(f"  'mouse': {[doc.doc_id for doc in inverted_index['mouse']]}")

    # Test query: cat AND dog
    print("\nQuery: 'cat dog AND' (expected: AP-002, AP-003)")
    br_test = BooleanRetrieval("cat dog AND")
    result = br_test.evaluate(inverted_index)
    print(f"Result: {[doc.doc_id for doc in result]}")

    # Test query: cat OR mouse
    print("\nQuery: 'cat mouse OR' (expected: AP-001, AP-002, AP-003, AP-004, AP-005)")
    br_test = BooleanRetrieval("cat mouse OR")
    result = br_test.evaluate(inverted_index)
    print(f"Result: {[doc.doc_id for doc in result]}")

    # Test query: cat AND-NOT dog
    print("\nQuery: 'cat dog NOT' (expected: AP-001, AP-005)")
    br_test = BooleanRetrieval("cat dog NOT")
    result = br_test.evaluate(inverted_index)
    print(f"Result: {[doc.doc_id for doc in result]}")

    # Test complex query: (cat AND dog) OR mouse
    print("\nQuery: 'cat dog AND mouse OR' (expected: AP-001, AP-002, AP-003, AP-004, AP-005)")
    br_test = BooleanRetrieval("cat dog AND mouse OR")
    result = br_test.evaluate(inverted_index)
    print(f"Result: {[doc.doc_id for doc in result]}")

    print(f"\n{'='*60}")
    print("TESTS COMPLETED!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    import sys

    # Check if user wants to run tests
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_query_functions()
        sys.exit(0)
    
    from inverted_index import InvertedIndex

    # Configuration
    data_path = './data'  # Path to the document collection
    queries_file = './BooleanQueries.txt'  # Path to file with boolean queries
    output_file = './Part_2.txt'  # Output file

    print("Creating and populating inverted index...")
    # Create and populate the inverted index
    inverted_index = InvertedIndex(data_path)
    inverted_index.populate(verbose=True)
    print(f"Inverted index created with {len(inverted_index.term_docs_dict)} terms")
    print(f"\nReading queries from {queries_file}...")
    # Read queries from file
    try:
        with open(queries_file, 'r') as f:
            queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"ERROR: Queries file not found: {queries_file}")
        exit(1)

    print(f"Found {len(queries)} queries to process")

    # Process each query and collect results
    results = []
    for i, query in enumerate(queries, 1):
        print(f"Processing query {i}/{len(queries)}: {query}")

        # Create BooleanRetrieval instance and evaluate
        br = BooleanRetrieval(query)
        try:
            result_docs = br.evaluate(inverted_index.term_docs_dict)

            # Extract doc_id names from Document objects
            doc_ids = [doc.doc_id for doc in result_docs]

            # Join with spaces
            result_line = ' '.join(doc_ids)
            results.append(result_line)

            print(f"  Found {len(doc_ids)} matching documents")
        except Exception as e:
            print(f"  ERROR evaluating query: {e}")
            results.append('')  # Empty line for failed query

    # Write results to output file
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w') as f:
        for result in results:
            f.write(result + '\n')

    print(f"Done! Results written to {output_file}")
    
