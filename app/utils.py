"""Utility methods."""
from flask import g

from connect import get_es
from config import max_docs


def get_all_docs():
    """Get all documents in the 'nssd' index with doc_type 'doc'."""
    if not hasattr(g, 'all_docs'):
        es = get_es()
        query = {"query": {"match_all": {}}, "size": max_docs}
        g.all_docs = es.search(
            'nssd', 'doc', query,
            _source_include=["violence_tags"])['hits']['hits']
    return g.all_docs
