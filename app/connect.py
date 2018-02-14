"""Methods to connect to external services."""
import os
from flask import g
from elasticsearch import Elasticsearch, RequestsHttpConnection

from config import max_docs


def _connect_es():
    """Connnect to AWS elasticsearch."""
    host = os.environ['ES_HOST']
    es = Elasticsearch(
        hosts=host,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def _connect_es_local():
    """Connnect to local elasticsearch."""
    es = Elasticsearch()
    return es


def get_es():
    """Open a new elasticsearch connection if there is none yet for the current application context."""
    if not hasattr(g, 'es_node'):
        g.es_node = _connect_es()
    return g.es_node


def get_all_docs():
    """Get all documents in the 'nssd' index with doc_type 'doc'."""
    if not hasattr(g, 'all_docs'):
        es = get_es()
        query = {"query": {"match_all": {}}, "size": max_docs}
        g.all_docs = es.search(
            'nssd', 'doc', query,
            _source_include=["violence_tags"])['hits']['hits']
    return g.all_docs
