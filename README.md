# The Lantern web application
## Part of The National School Security Database (NSSD)
The Lantern is a Flask web application that seeks to help parents, teachers, students, school staff, mental health professionals, educational policy analysts, and researchers better understand the connection between various behavioral patterns and youth violence. This knowledge can help develop individual student or school wide anti-violence intervention programs.

## Usage: Python 2.7
The Lantern is currently deployed as a Heroku [app](https://dashboard.heroku.com/apps/nssd). It can also be run locally (e.g., for testing); the easiest way to do so is through a pip virtualenv using the requirements listed in `requirements.txt`:

1. Create virtual environment (optional): `virtualenv venv`
1. Activate virtual environment (optional: `source venv/bin/activate`
1. Install Python requirements: `pip install -r requirements.txt`
1. Set environment variables (these can be copied from the Heroku app)
1. Run the application: `python run.py` or `gunicorn app:app`

## Services
The Lantern uses Bonsai ElasticSearch (via the [Python ElasticSearch Client](http://elasticsearch-py.readthedocs.io/en/master/)) to identify potential risk factors relating to school violence based on indexed text documents. Management of the ElasticSearch index and associated documents can be found in [this](https://github.com/NoSchoolViolence/search-app-documents) repository.

Persistence is managed with a Heroku Postgres instance through [SQLAlchemy](https://www.sqlalchemy.org/).

## Methodology
The Lantern estimates the relevance of each of several forms of school violence to a given context in several steps:
1. Tag text documents pertinent to school violence with relevant forms of school violence
1. Index documents and associated tags in ElasticSearch
1. Context is specified as a search string (e.g., "failing school", "heavy drug usage") via a form in the web application
1. Identify a subset of documents relevant to the context search string
1. Count violence tags across the relevant subset of documents
1. Normalize violence tag frequencies against their frequencies over all documents
1. Display the resulting tag-specific relevance scores in the web application
