import flask
import werkzeug.exceptions
import mechanic.exceptions


def api_enforce(request=None, response=None, many=False, code=200, auth_bearer=False, request_headers=None, response_header=None):
    def api_enforce_decorator(f):
        def wrapper(*args, **kwargs):
            if auth_bearer and not flask.request.headers.get('Authorization', '').startswith('Bearer'):
                msg = 'Authorization Bearer token not present in header. Expected format: Authorization: Bearer <token>'
                raise werkzeug.exceptions.Unauthorized(msg)
            embed = flask.request.args.get('embed', '').split(',')
            for k, v in flask.request.args.items():
                if k in args or k in kwargs.keys():
                    kwargs[k] = v
            etag = None

            if request:
                request_schema = request(many=many, context={'embed': embed})
                obj, errors = request_schema.load(flask.request.get_json())
                resp = f(*args, serialized_request_data=obj, **kwargs)
            else:
                resp = f(*args, **kwargs)

            resp_body = resp
            resp_headers = {}
            if response:
                response_schema = response(many=many, context={'embed': embed})

                if isinstance(resp, tuple):
                    if len(resp) != 2:
                        error_msg = 'The return value from endpoints must either be a single item with the response ' \
                                    'body, or a tuple of format (<response_body>, <response_headers>). Failing ' \
                                    'method: %s' % str(f)
                        raise mechanic.exceptions.MechanicDeveloperError(error_msg)
                    resp_body = resp[0]
                    resp_headers = resp[1]

                try:
                    resp_body, errors = response_schema.dump(resp_body)
                except TypeError:
                    error_msg = 'Unable to deserialize response from method %s. Response body was unexpected type %s' \
                                % (str(f), type(resp_body))
                    raise mechanic.exceptions.MechanicDeveloperError(error_msg)
            return flask.make_response(flask.jsonify(resp_body), code, resp_headers)
        return wrapper
    return api_enforce_decorator
