"""HTML views for web app."""
from flask import render_template, request

from connect import get_es
from utils import get_all_docs
from assess import get_violence_ratios, get_matches
from app import app


@app.route('/', methods=['GET'])
def index():
    """Render index template."""
    return render_template('index.html')


@app.route('/ABD')
def serve_abd():
    """Render dictionary template."""
    return render_template('ABD.html')


@app.route('/about')
def serve_about():
    """Render the about template."""
    return render_template('about.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    """Render the search template."""
    es = get_es()
    num_hits_search = -1
    resp = []

    if request.method == "POST":
        # Get a count of documents with matching search tags
        context_terms = request.form['search-terms']
        resp = get_matches(es, context_terms)
        num_hits_search = len(resp)

    ratios = get_violence_ratios(get_all_docs(), resp)
    return render_template(
        'search.html', page='search', num_hits_search=num_hits_search,
        ratios=ratios
    )


@app.errorhandler(401)
def custom_401(error):
    """Render 401 error template."""
    return render_template('401.html'), 401


@app.errorhandler(404)
def not_found(error):
    """Render 404 error template."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Render 500 error template."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run()
