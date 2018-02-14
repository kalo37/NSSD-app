"""Assess conditional violence-type relevance."""
import pandas as pd
from collections import defaultdict

from app import db
from models import Search

from config import max_docs


def get_violence_ratios(all_docs, relevant_docs):
    """Calculate the relevance of various forms of violence to a given search term.

    Calculates relevance by normalizing search-specific violence tag counts with the total
    violence tag counts across all indexed documents.

    Arguments:
        - all_docs (list[dict]): list of all indexed documents
        - response (list[dict]): list of documents relevant to a particular search term
    """
    # calculate total violence tag counts across all indexed documents
    sum_violence_tags = count_violence_tags(all_docs)
    sum_violence_tags_df = pd.DataFrame.from_dict(
        sum_violence_tags, orient='index')
    sum_violence_tags_df.columns = ['total_counts']

    # calculate violence tag counts specific to a given search term (specified in request form)
    if len(relevant_docs) > 0:
        n_violence_tags = count_violence_tags(relevant_docs)
        n_violence_tags_df = pd.DataFrame.from_dict(
            n_violence_tags, orient='index')
    else:
        n_violence_tags_df = sum_violence_tags_df.copy()
        n_violence_tags_df.ix[:, 0] = 0
    n_violence_tags_df.columns = ['query_counts']

    # calculate relevancy as context-specific tag counts normalized by total tag counts
    violence_ratios = pd.merge(
        sum_violence_tags_df, n_violence_tags_df,
        left_index=True, right_index=True)
    violence_ratios['ratio'] = violence_ratios.query_counts /\
        violence_ratios.total_counts

    # clean table for output
    violence_ratios.sort_values('ratio', ascending=False, inplace=True)
    violence_ratios['categories'] = pd.cut(
        violence_ratios.ratio, [0, .1, .2, 1], labels=['low', 'medium', 'high'])
    violence_ratios['category_colors'] = pd.cut(
        violence_ratios.ratio, [0, .1, .2, 1], labels=[
            '250, 230, 10', '250, 130, 30', '250, 30, 30'])
    violence_ratios.ratio = (violence_ratios.ratio * 100).map(
        '{:,.1f}%'.format)

    return violence_ratios


def count_violence_tags(docs):
    """Tabulate the count of each violence tag in a list of elasticsearch documents.

    Arguments:
        - docs (list[dict]): list of relevant documents returned by elasticsearch
    """
    violence_tags_counts = defaultdict(float)
    for doc in docs:
        for tag in doc['_source']['violence_tags']:
            violence_tags_counts[tag] += doc['_score']
    return violence_tags_counts


def get_matches(es, context_terms):
    """Read search terms from the current request from and return relevant documents from elasticsearch index.

    Arguments:
        - es: elasticsearch client connection
        - context_terms (list[str]): list of terms indicating the context under which to calculate violence-type relevance
    """
    # save search to db
    _search = Search('unauthenticated', context_terms)
    db.session.add(_search)
    db.session.commit()

    # search elasticsearch index
    query = {"query": {"bool": {
        "should": [
            {"match": {"search_tags": {
                'query': s.strip(),
                "fuzziness": "AUTO",
                "minimum_should_match": "50%"}}}
            for s in context_terms.split(';')]}},
        "size": max_docs}
    response = es.search(
        'nssd', 'doc', query,
        _source_include=["violence_tags"])

    # return only the hits, removing search meta data
    return response['hits']['hits']
