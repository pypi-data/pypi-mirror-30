import pkg_resources
import re

import falcon
import flask
import werkzeug.exceptions
import mechanic.exceptions
from apispec import APISpec


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


class APIContractException(Exception):
    pass


class MechanicAPIResource(object):
    def __init__(self, path, params=None):
        self.path = path
        self.params = params


class MechanicAPISpec(APISpec):
    def __init__(self, *args, security_schemes=None, **kwargs):
        super(MechanicAPISpec, self).__init__(*args, **kwargs)
        self._security_schemes = security_schemes if security_schemes else dict()

    def to_dict(self):
        ret = {
            'info': self.info,
            'paths': self._paths,
            'tags': self._tags
        }

        if self.openapi_version.version[0] == 2:
            ret['swagger'] = self.openapi_version.vstring
            ret['definitions'] = self._definitions
            ret['parameters'] = self._parameters

        elif self.openapi_version.version[0] == 3:
            ret['openapi'] = self.openapi_version.vstring
            ret['components'] = {
                'schemas': self._definitions,
                'parameters': self._parameters,
                'securitySchemes': self._security_schemes
            }

        ret.update(self.options)
        return ret

    def add_security_scheme(self, scheme_name, scheme_obj):
        self._security_schemes[scheme_name] = scheme_obj


class MechanicAPI(object):
    class OpenAPIJsonResource(MechanicAPIResource):
        def on_get(self, req, resp):
            resp.media = self.params['spec'].to_dict()

    class OpenAPIYamlResource(MechanicAPIResource):
        def on_get(self, req, resp):
            resp.media = self.params['spec'].to_yaml()

    class OpenAPIDocsResource(MechanicAPIResource):
        def on_get(self, req, resp):
            resp.content_type = 'text/html'

            filepath = pkg_resources.resource_filename(__name__, 'static/swagger/swagger-ui-index.html')
            with open(filepath, 'r') as f:
                file_data = f.read().replace('{{TITLE}}', self.params['title'])
                file_data = file_data.replace('{{THEME}}', self.params['theme'])
                file_data = file_data.replace('{{URL}}', f'{req.protocol}://{req.netloc}')
                resp.body = file_data

    class StaticResource(MechanicAPIResource):
        def on_get(self, req, resp, filename):
            resp.status = falcon.HTTP_200

            if filename.endswith('.html'):
                resp.content_type = 'text/html'
            if filename.endswith('.css'):
                resp.content_type = 'text/css'
            if filename.endswith('.js'):
                resp.content_type = 'application/javascript'

            filepath = pkg_resources.resource_filename(__name__, 'static/swagger/' + filename)
            with open(filepath, 'r') as f:
                resp.body = f.read()

    def __init__(self, title='Mechanic Project', version='1.0.0', security_schemes=None,
                 docs_path='/', docs_theme='swagger-ui', **kwargs):
        """
        :param title:
        :param version:
        :param openapi_version:
        :param security_schemes:
        :param docs_path: defaults to '/'
        :param docs_theme: material, feeling-blue, flattop, monokai, muted, newspaper, outline
        :param kwargs:
        """
        self.spec = MechanicAPISpec(
            title=title,
            version=version,
            plugins=[
                'apispec.ext.marshmallow',
            ],
            openapi_version='3.0.0',
            **kwargs
        )
        self.api = falcon.API()
        self.resource_map = dict()
        self.method_map = dict()
        self.security_schemes = security_schemes if security_schemes else dict()

        for k, v in self.security_schemes.items():
            self.spec.add_security_scheme(k, v)

        self.add_route(self.OpenAPIJsonResource('/openapi.json', {'spec': self.spec}), document=False)
        self.add_route(self.OpenAPIYamlResource('/openapi.yaml', {'spec': self.spec}), document=False)
        self.add_route(self.OpenAPIDocsResource(docs_path, {'title': title, 'theme': docs_theme}), document=False)
        self.add_route(self.StaticResource('/static/swagger/{filename}'), document=False)

    @staticmethod
    def _serialize_resp(req, resp, resource, schema=None, success_status_code=falcon.HTTP_200, **kwargs):
        if schema:
            resp.media = schema(**kwargs).dump(resp.media).data
            resp.status = success_status_code

    @staticmethod
    def _deserialize_req(req, resp, resource, params, schema=None, **kwargs):
        if schema:
            params['loaded_schema'] = schema(**kwargs).load(req.media).data

    @staticmethod
    def _check_parameter(req, resp, resource, params, param_name=None, param_in=None, param_required=False):
        if param_in == 'query' and param_required and (param_name not in req.params.keys()):
            raise APIContractException(f'Missing query parameter {param_name}')
        elif param_in == 'header' and param_required and (not req.get_header(param_name)):
            raise APIContractException(f'Missing header {param_name}')

    def method_tags(self, tags):
        for tag in tags:
            self.spec.add_tag(tag)

        def wrapper(f):
            if not self.method_map.get(f.__qualname__):
                self.method_map[f.__qualname__] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('tags'):
                self.method_map[f.__qualname__]['tags'] = tags
            return f
        return wrapper

    def tag(self, tag):
        self.spec.add_tag(tag)

        def wrapper(f):
            return f
        return wrapper

    def add_route(self, resource, document=True):
        self.api.add_route(resource.path, resource)
        if document:
            self.resource_map[str(resource.__class__.__name__)] = resource.path

            operations = dict()
            curly_brace_regex = r'\{([^}]+)\}'
            matches = re.findall(curly_brace_regex, resource.path)
            for match in matches:
                self.spec.add_parameter(match, location='path', required=True)

            for m in dir(resource):
                for hm in falcon.COMBINED_METHODS:
                    if m == f'on_{hm.lower()}':
                        op_method = resource.__class__.__name__ + '.' + m

                        if not self.method_map.get(op_method):
                            self.method_map[op_method] = dict()

                        for match in matches:
                            if not self.method_map.get(op_method, {}).get('parameters'):
                                self.method_map[op_method]['parameters'] = dict()

                            self.method_map[op_method]['parameters'][match] = {
                                'name': match,
                                'in': 'path',
                                'required': True
                            }

                        operations[hm.lower()] = self.method_map[op_method]

            self.spec.add_path(resource.path, operations=operations)

    def security(self, security):
        def hook(f):
            if not self.method_map.get(f.__qualname__):
                self.method_map[f.__qualname__] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('security'):
                self.method_map[f.__qualname__]['security'] = security

            if security == []:
                return f

            for s in security:
                for scheme_name, scheme_val in s.items():
                    if not self.security_schemes.get(scheme_name):
                        raise APIContractException(f'Security name {scheme_name} not defined in Mechanic object.')

                    scheme_obj = self.security_schemes.get(scheme_name, {})

                    if scheme_obj['type'] == 'http' and scheme_obj.get('scheme') == 'bearer':
                        # TODO add validation for string starting with 'Bearer'
                        f = falcon.before(self._check_parameter,
                                          param_name='Authorization',
                                          param_in='header',
                                          param_required=True)(f)
                    elif scheme_obj['type'] == 'http' and scheme_obj.get('scheme') == 'basic':
                        # TODO add validation for string starting with 'Basic'
                        f = falcon.before(self._check_parameter,
                                          param_name='Authorization',
                                          param_in='header',
                                          param_required=True)(f)
                    elif scheme_obj['type'] == 'apiKey':
                        f = falcon.before(self._check_parameter,
                                          param_name=scheme_obj['name'],
                                          param_in=scheme_obj['in'],
                                          param_required=True)(f)
            return f
        return hook

    def parameter(self, param):
        def hook(f):
            if not self.method_map.get(f.__qualname__):
                self.method_map[f.__qualname__] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('parameters'):
                self.method_map[f.__qualname__]['parameters'] = dict()

            self.method_map[f.__qualname__]['parameters'][param['name']] = param
            self.method_map[f.__qualname__]['operationId'] = f.__qualname__.split('.')[-1]
            self.spec.add_parameter(param['name'], location=param['in'], required=param.get('required'))
            f = falcon.before(self._check_parameter,
                              param_name=param['name'],
                              param_in=param['in'],
                              param_required=param.get('required', False))(f)
            return f
        return hook

    def request(self, schema, schema_name=None, content='application/json', **kwargs):
        schema_name = schema_name if schema_name else schema.__name__

        def hook(f):
            if not self.method_map.get(f.__qualname__):
                self.method_map[f.__qualname__] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('parameters'):
                self.method_map[f.__qualname__]['parameters'] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('requestBody'):
                self.method_map[f.__qualname__]['requestBody'] = dict()

            self.spec.definition(schema_name, schema=schema)
            self.method_map[f.__qualname__]['requestBody'] = {
                'content': {
                    f'{content}': {
                        'schema': {
                            '$ref': f'#/components/schemas/{schema_name}'
                        }
                    }
                }
            }

            f = falcon.before(self._deserialize_req, schema=schema, **kwargs)(f)
            return f
        return hook

    def response(self, schema, schema_name=None, success_status_code=falcon.HTTP_200, content='application/json', **kwargs):
        schema_name = schema_name if schema_name else schema.__name__

        def hook(f):
            if not self.method_map.get(f.__qualname__):
                self.method_map[f.__qualname__] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('parameters'):
                self.method_map[f.__qualname__]['parameters'] = dict()

            if not self.method_map.get(f.__qualname__, {}).get('response'):
                self.method_map[f.__qualname__]['responses'] = dict()

            self.method_map[f.__qualname__]['responses'] = {
                f'{str(success_status_code.split(" ")[0])}': {
                    'content': {
                        f'{content}': {
                            'schema': {
                                '$ref': f'#/components/schemas/{schema_name}'
                            }
                        }
                    }
                }
            }
            self.spec.definition(schema_name, schema=schema)
            f = falcon.after(self._serialize_resp, schema=schema, success_status_code=success_status_code, **kwargs)(f)
            return f
        return hook