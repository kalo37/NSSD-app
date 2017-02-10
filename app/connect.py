import os
from flask import g
from elasticsearch import Elasticsearch, RequestsHttpConnection

# Connnect to AWS elasticsearch
def _connect_es():
    host = os.environ['ES_HOST']
    es = Elasticsearch(
        hosts=host,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    return es


# Connnect to local elasticsearch
def _connect_es_local():
    es = Elasticsearch()
    return es


# Opens a new elasticsearch connection if there is none yet for the
# current application context
def get_es():
    if not hasattr(g, 'es_node'):
        g.es_node = _connect_es()
    return g.es_node


def get_all_docs():
    if not hasattr(g, 'all_docs'):
        es = get_es()
        query = {"query": {"match_all": {}}, "size": 100}
        g.all_docs = es.search(
            'nssd', 'doc', query,
            _source_include=["violence_tags"])['hits']['hits']
    return g.all_docs
