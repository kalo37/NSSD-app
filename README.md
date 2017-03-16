# The Lantern web application
## Part of The National School Security Database (NSSD)
The Lantern is a Flask web application that seeks to help parents, teachers, students, school staff, mental health professionals, educational policy analysts, and researchers better understand the connection between various behavioral patterns and youth violence. This knowledge can help develop individual student or school wide anti-violence intervention programs.

## Usage
The Lantern is currently deployed as a Heroku [app](https://dashboard.heroku.com/apps/nssd). It can also be run locally (e.g., for testing); the easiest way to do so is through a pip virtualenv using the requirements listed in `requirements.txt`:

1. `$ virtualenv venv`
1. `$ source venv/bin/activate`
1. `$ pip install -r requirements.txt`
1. Set environment variables (these can be copied from the Heroku app) for reference by the Flask app
1. `$ python run.py`

## Mechanics
The Lantern uses Bonsai ElasticSearch (via the [Python ElasticSearch Client](http://elasticsearch-py.readthedocs.io/en/master/)) to identify potential risk factors relating to school violence based on indexed text documents. Management of the ElasticSearch index and associated documents can be found in [this](https://github.com/NoSchoolViolence/search-app-documents) repository.

Persistence is managed with a Heroku Postgres instance through [SQLAlchemy](https://www.sqlalchemy.org/), and user authentication is managed through [Stormpath](https://stormpath.com/).
