"""Methods to connect to external services."""
import os
from flask import g
from elasticsearch import Elasticsearch, RequestsHttpConnection


def _connect_es():
    """Connnect to AWS elasticsearch."""
    host = os.environ['ES_HOST']
    es = Elasticsearch(
        hosts=host,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


def get_es():
    """Open a new elasticsearch connection if there is none yet for the current application context."""
    if not hasattr(g, 'es_node'):
        g.es_node = _connect_es()
    return g.es_node
