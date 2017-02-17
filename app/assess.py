import pandas as pd
from collections import defaultdict
from flask import request

from config import max_docs


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

    # Clean table for output
    violence_ratios.sort_values('ratio', ascending=False, inplace=True)
    violence_ratios.ratio = (violence_ratios.ratio * 100).map(
        '{:,.1f}%'.format)
    violence_ratios.columns = [
        '# total documents', '# matches', 'Risk score']
    violence_ratios['Types of Violence (CDC,WHO, NIH, DOJ)'] = \
        violence_ratios.index
    cols = list(violence_ratios.columns)
    cols = [cols.pop()] + cols
    return violence_ratios[cols]


def count_violence_tags(resp):
    violence_tags_counts = defaultdict(float)
    for doc in resp:
        for tag in doc['_source']['violence_tags']:
            violence_tags_counts[tag] += doc['_score']
    return violence_tags_counts

def get_matches(es):
    cname = request.form['search-terms']
    query = {"query": {"bool": {
        "should": [
            {"match": {"search_tags": {
                'query': s.strip(),
                "minimum_should_match": "50%"}}}
            for s in cname.split(';')]}},
        "_source": "search_tags", "size": max_docs}
    resp = es.search(
        'nssd', 'doc', query,
        _source_include=["violence_tags"])['hits']['hits']
    return resp
