*****************************************************************************************
:fire:flask-json-api:fire:: Flask boilerplate setup code for REST application/json API's
*****************************************************************************************

The **Flask JSON API** package provides boilerplate code for setting up REST based apps
written with `Flask <https://github.com/pallets/flask>`_.



Installing flask-json-api
=========================

.. code-block:: bash

  pip install flask-json-api


Using Flask JSON API
====================

Using **Flak JSON API** is as easy as initiating it with the Flask app instance:

.. code-block:: python

    from flask import Flask

    from flask_json_api import FlaskJsonApi

    app = Flask(__name__)

    flask_json_api = FlaskJsonApi(app)

How it works
============

This package requires the ``application/json content-type`` header, or else an HTTP error will be returned:

.. code-block:: python

    import requests

    # providing the application/json content type will succeed
    url = 'http://localhost:5000/api'
    headers = {'Content-Type': 'application/json'}

    r = requests.get(url, headers=headers)

    assert r.status_code == 200

    # not providing the application/json content type will fail
    url = 'http://localhost:5000/api'

    r = requests.get(url)

    assert r.status_code == 415


Register expected and unexpected exception types:
=================================================
Although all errors should be returned as JSON, you can register different exception types as:
 * ``Expected Errors`` - will return **400** http error code (and logged with WARNING level)
 * ``Unexpected Errors`` - will return **500** http error code (and logged with ERROR level)

.. code-block:: python

    class ExpectedError(Exception):
    """Expected error, such as Data Validation Error"""

    class UnexpectedError(Exception):
        """Unexpected error, such as database is not accessible"""

    flask_json_api.register_expected_exception(ExpectedError)
    flask_json_api.register_unexpected_exception(UnexpectedError)

Whitelisting paths that do not require application/json
-------------------------------------------------------
Whenever the ``flask.request.path`` starts with any of these ``exclude_paths``, then the
application/json header won't be required.

.. code-block:: python

    flask_json_api.set_application_json_exclude_paths(exclude_paths=['/home'])

    # Please note that if the exclude_paths will contain '/',
    # then no path will require the application/json content-type