====================
local-document-store
====================

This package was written in an attempt to replicate some of the functionality of the popular document store MongoDB. It provides methods to add and store JSON documents, search those documents using an example JSON query, and modify those documents using a search query and a replacement document. 

=============
Example Usage
=============


>>> from lds import DocStore
>>> store = DocStore()
>>> store.add('{"name": "oski", "details": {"school": "california", "year": "senior"}}') #add string
True
>>> store.add('{"name": "harry", "details": {"school": "washington", "year": "junior"}}') #add dict
True
>>> store.search({"year": "junior"})
[{'name': 'harry', 'details': {'year': 'junior', 'school': 'washington'}}]
>>> store.update({"year": "senior"}, {"year": "junior"}, exact=True)
>>> store.search({"year": "junior"})
[{'name': 'oski', 'details': {'year': 'junior', 'school': 'california'}},\
{'name': 'harry', 'details': {'year': 'junior', 'school': 'washington'}}]

Full documentation can be found at: http://local-document-store.readthedocs.io/en/latest/lds.html

============================
Who should use this library?
============================

This package is not intended for use in production, as of yet. For more comprehensive methods and more performant queries, one should use MongoDB itself. This package is useful for quickly storing a series of documents and querying/modifying them, and therefore may be useful in a proof-of-concept or early-stage application.
