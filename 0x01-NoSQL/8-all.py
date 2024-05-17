#!/usr/bin/env python3

"""Write a Python function that lists all documents in a collection:
Prototype: def list_all(mongo_collection):
Return an empty list if no document in the collection
mongo_collection will be the pymongo collection object
"""

import pymongo


def list_all(mongo_collection):
    """Return list of all docs in a collection"""
    if not mongo_collection:
        return []
    return list(mongo_collection.find())
