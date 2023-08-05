import sys
from typing import Set, List, Type

from flask import Flask, request

__version__ = '1.0.0'

import logging
import flask
from werkzeug.exceptions import HTTPException, NotAcceptable, UnsupportedMediaType, default_exceptions


logger = logging.getLogger(__name__)


class FlaskJsonApi(object):
    def __init__(self, app: Flask=None):
        self.app = app
        self._application_json_exclude_paths = set()
        if app:
            self.init_app(app)

    def init_app(self, app: Flask):
        self.app = app
        self.app.before_request(self._validate_content_type_is_application_json)
        for code in default_exceptions.keys():
            self.app.register_error_handler(code, FlaskJsonApi._http_error_handling)
        self.app.register_error_handler(Exception, FlaskJsonApi._global_error_handling)

    def register_expected_exception(self, error: Type[Exception]):
        """
        Register expected exception to be caught (such as a validation error)
        :param error: Type of the exception that should be caught
        """
        self.app.register_error_handler(error, FlaskJsonApi._expected_error_handling)

    def register_unexpected_exception(self, error: Type[Exception]):
        """
        Register unexpected exception to be caught (such as database is not reachable)
        :param error: Type of the exception that should be caught
        """
        self.app.register_error_handler(error, FlaskJsonApi._unexpected_error_handling)

    def set_application_json_exclude_paths(self, exclude_paths: List[str]):
        """
        Set the list of relative paths for which no application/json header is required.
        Whenever a ``request.path`` starts with any of these ``exclude_paths``, then the
        application/json header won't be required.
        :param exclude_paths: list of relative paths
        """
        self._application_json_exclude_paths = set(exclude_paths) if exclude_paths is not None else set()

    def _validate_content_type_is_application_json(self):
        for path in self._application_json_exclude_paths:
            if request.path.startswith(path):
                return

        content_type = flask.request.headers.get('Content-Type')
        if not content_type:
            raise UnsupportedMediaType('Please provide an application/json Content-Type header')

        if 'application/json' not in content_type:
            raise NotAcceptable('Please specify application/json in the Content-Type header')

    @staticmethod
    def _expected_error_handling(error: Exception) -> flask.Response:
        code = 400
        error_message = str(error)
        logger.warning(error_message, exc_info=sys.exc_info())
        response = FlaskJsonApi._create_response(code, error_message)
        return response

    @staticmethod
    def _unexpected_error_handling(error: Exception) -> flask.Response:
        code = 500
        description = 'Unexpected error'
        error_message = str(error)
        FlaskJsonApi._log_error(error_message)
        response = FlaskJsonApi._create_response(code, error_message, description)
        return response

    @staticmethod
    def _log_error(error_message: str):
        logger.error(error_message, exc_info=sys.exc_info())

    @staticmethod
    def _http_error_handling(error: HTTPException) -> flask.Response:
        code = error.code
        description = error.description
        error_message = str(error)
        FlaskJsonApi._log_error(error_message)
        response = FlaskJsonApi._create_response(code, error_message, description)
        return response

    @staticmethod
    def _global_error_handling(error: Exception) -> flask.Response:
        code = 500
        description = default_exceptions[500].description
        error_message = str(error)
        FlaskJsonApi._log_error(error_message)
        response = FlaskJsonApi._create_response(code, error_message, description)
        return response

    @staticmethod
    def _create_response(code: int, message: str, description=None) -> flask.Response:
        result = dict(message=message)
        if description:
            result['description'] = description
        response = flask.jsonify(result)
        response.status_code = code
        return response
