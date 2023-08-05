import json
import itertools


class DocStore:
    """ The main class for this module, which stores and operates on documents.

    This class attempts to replicate some of the functionality of the popular
    document store MongoDB. It provides method to add and store JSON documents,
    search those documents using an example JSON query, and modify those
    documents using a search query and a replacement document.
    """
    def __init__(self):
        """The standard initialization method, initializes the list where 
        documents will be stored.

        Parameters
        ----------
        None 
        """
        self._documents = []

    def add(self, doc):
        """Adds a document to the list holding the documents.

        Constructs a tuple of a document, passed in as a parameter, and a set
        of tuples representing the (key: value) pairings of the document (to be
        used for querying the documents), and appends aforementioned tuple to
        the list of documents initialized in __init__.
        
        >>> store = DocStore()
        >>> store.add('{"name": "oski", "school": "california"}') #string
        True
        >>> store.add({'name': 'harry', 'school': 'washington'}) #dict
        True

        Parameters
        ----------
        doc: str/dict
            doc, the document to be added, can be passed in as a string
            or a Python dictionary.

        Returns
        -------
        True: if add operation was successfully completed.
        """
        doc_json = self.__convert_str_json(doc)
        document_base_pairs = set(self.__key_val_extract(doc_json))
        self._documents += (document_base_pairs, doc_json),
        return True

    def add_many(self, docs):
        """Adds multiple documents to the class' internal list of documents.

        Calls the `add` function over the list of documents passed in.

        Parameters
        ----------
        docs: list
            the list of documents, which can be strings or Python dictionaries.

        Returns
        -------
        True: if all add operations were successfully completed.
        """

        for doc in docs:
            self.add(doc)
        return True

    def search(self, query):
        """Searches for documents that match the query passed in.

        Converts the query passed in as a parameter to a set of tuples
        representing the (key: value) pairings of the document, and checks if
        the set of tuples of the query parameter is a subset of any of the sets
        of tuples of the documents currently in the store. If it finds matching
        documents, it returns them as a list.
        
        >>> store.add({'name': 'harry', 'school': 'washington'})
        True
        >>> store.add('{"name": "oski", "school": "california"}')
        True
        >>> store.search({'name': 'oski'})
        [{'name': 'oski', 'school': 'california'}]

        Parameters
        ----------
        query: str/dict
            the query that the list of documents will be matched against.

        Returns
        -------
        list: of documents that match the query passed in.
        """
        query_json = self.__convert_str_json(query)
        query_base_pairs = set(self.__key_val_extract(query_json))
        return [raw for pairs, raw in self._documents if query_base_pairs <= pairs]

    def update(self, match, new, exact=False):
        """Updates documents with the new values passed in to the documents that
        match the query passed in.

        Searches the document with the same logic as described in `search`, and
        updates documents that match. The `exact` parameter determines what 
        type of update will be performed. If `exact` is False (its default value),
        the old document will simply be merged with the new one using
        `{**old, **new}`. If `exact` is True, it is important to pass in a
        single (key: value) pairing to both the `match` and `new` parameter;
        the document will be iterated over and only when the match is found in
        the current document will the value be updated.

        .note:: if you are updating a nested value of the document, you must
                use `exact`=True. Python's merge operation, as detailed above,
                will not accurately merge nested documents.

        >>> store.add('{"name": "oski", "details": {"school": "california", "year": "senior"}}')
        True
        >>> store.add('{"name": "harry", "details": {"school": "washington", "year": "junior"}}')
        True
        >>> store.search({"year": "junior"})
        [{'name': 'harry', 'details': {'year': 'junior', 'school': 'washington'}}]
        >>> store.update({"year": "senior"}, {"year": "junior"}, exact=True)
        >>> store.search({"year": "junior"})
        [{'name': 'oski', 'details': {'year': 'junior', 'school': 'california'}},\
        {'name': 'harry', 'details': {'year': 'junior', 'school': 'washington'}}]

        Parameters
        ----------
        match: str/dict
            the query that the list of documents will be matched against.
        new: str/dict
            the document which will be merged into the existing, matching document.

        Returns
        -------
        True: if the update was performed successfully.

        """
        match_json = self.__convert_str_json(match)
        new_json = self.__convert_str_json(new)

        if exact:
            if len(match_json) != 1 or len(new_json) != 1:
                return
            match_pair = list(match_json.items())[0]
            new_pair = list(new_json.items())[0]

        match_base_pairs = set(self.__key_val_extract(match_json))
        for i, item in enumerate(self._documents):
            pairs, raw = item
            if match_base_pairs <= pairs:
                if exact:
                    updated_doc = self.__update_exact_helper(raw, match_pair, new_pair)
                else:
                    updated_doc = {**raw, **new_json}
                updated_doc_base_pairs = set(self.__key_val_extract(updated_doc))
                self._documents[i] = (updated_doc_base_pairs, updated_doc)

    def __convert_str_json(self, item):
        """Converts a string to a dictionary if it is not already a dictionary."""
        if isinstance(item, str):
            return json.loads(item)
        return item

    def __update_exact_helper(self, prev, match, new):
        """Helper method to update the document, as described in `update`."""
        updated = prev.copy()
        new_key, new_val = new
        for key, value in prev.items():
            if isinstance(value, dict):
                updated[key] = self.__update_exact_helper(value, match, new)
            elif isinstance(value, list):
                updated[key] = [self.__update_exact_helper(item, match, new) for item in value]
            elif (key, value) == match and key == new_key:
                updated[key] = new_val
        return updated

    def __key_val_extract(self, doc):
        """Helper method to extract (key: value) pairings from the document, as described in `add`."""
        extracted_pairs = []
        for key, value in doc.items():
            if isinstance(value, dict):
                extracted_pairs += (key, 'nested_json'),
                extracted_pairs.extend(self.__key_val_extract(value))
            elif isinstance(value, list):
                extracted_pairs += (key, 'nested_list'),
                pairs_from_list = [self.__key_val_extract(item) for item in value]
                extracted_pairs.extend(list(itertools.chain(*pairs_from_list)))
            else:
                extracted_pairs += (key, value),
        return extracted_pairs
