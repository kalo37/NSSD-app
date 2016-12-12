import os
from flask import Flask, render_template, request, jsonify, g
from elasticsearch import Elasticsearch, RequestsHttpConnection
from flask_bootstrap import Bootstrap
from flask_sslify import SSLify
from flask_stormpath import StormpathManager, login_required, user
from collections import defaultdict
import pandas as pd

app = Flask(__name__)
sslify = SSLify(app)
Bootstrap(app)
app.config.from_object(os.environ['APP_SETTINGS'])

# OAuth credentials and configuration
app.config['SECRET_KEY'] = os.environ['STORMPATH_SECRET_KEY']
app.config['STORMPATH_API_KEY_ID'] = os.environ['STORMPATH_API_KEY_ID']
app.config['STORMPATH_API_KEY_SECRET'] = os.environ['STORMPATH_API_KEY_SECRET']
app.config['STORMPATH_APPLICATION'] = os.environ['STORMPATH_APPLICATION']
app.config['STORMPATH_ENABLE_MIDDLE_NAME'] = False
app.config['STORMPATH_ENABLE_FORGOT_PASSWORD'] = True
stormpath_manager = StormpathManager(app)


@app.context_processor
def inject_user():
    return dict(is_authenticated=user.is_authenticated)


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


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():

    es = get_es()
    num_hits_search = -1
    resp = []

    if request.method == "POST":

        # Get a count of documents with matching search tags
        cname = request.form['search-terms']
        query = {"query": {"terms": {
            "search_tags": [s.strip() for s in cname.split(';')]}},
            "_source": "search_tags", "size": 100}
        resp = es.search(
            'nssd', 'doc', query,
            _source_include=["violence_tags"])['hits']['hits']
        num_hits_search = len(resp)

    ratios = get_violence_ratios(get_all_docs(), resp).sort_values(
        'ratio', ascending=False)
    return render_template(
        'search.html', page='search', num_hits_search=num_hits_search,
        ratios=ratios.to_html(classes='table table-hover table-bordered'))


def get_violence_ratios(all_docs, resp):
    sum_violence_tags = count_violence_tags(all_docs)
    sum_violence_tags_df = pd.DataFrame.from_dict(
        sum_violence_tags, orient='index')
    sum_violence_tags_df.columns = ['total_counts']

    if len(resp) > 0:
        n_violence_tags = count_violence_tags(resp)
        n_violence_tags_df = pd.DataFrame.from_dict(
            n_violence_tags, orient='index')
    else:
        n_violence_tags_df = sum_violence_tags_df.copy()
        n_violence_tags_df.ix[:, 0] = 0
    n_violence_tags_df.columns = ['query_counts']

    violence_ratios = pd.merge(
        sum_violence_tags_df, n_violence_tags_df,
        left_index=True, right_index=True)
    violence_ratios['ratio'] = violence_ratios.query_counts /\
        violence_ratios.total_counts
    return violence_ratios


def count_violence_tags(resp):
    violence_tags_counts = defaultdict(int)
    for doc in resp:
        for tag in doc['_source']['violence_tags']:
            violence_tags_counts[tag] += 1
    return violence_tags_counts


@app.errorhandler(401)
def custom_401(error):
    return render_template('401.html'), 401


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
