"""radleyberg-printing-press main app module

The Radleyberg printing press is a Flask server that transforms HTTP
requests into OpenShift templates.
"""
import copy

import flask
from flask import views
import yaml


class ConfigWrapper():
    """A helper for dealing with the configuration file"""
    def __init__(self, override=None):
        if override is None:
            self.config = yaml.load(open('config.yaml').read())
        else:
            self.config = override

    def has_version(self, version):
        """Does the config know about this version?"""
        return version in self.config

    def get_version(self, version, default=None):
        ret = default
        if version in self.config:
            ret = version
        return ret

    def get_parameters(self, version):
        """Return the parameters for a given version"""
        return copy.deepcopy(self.config[version]['parameters'])

    def get_template(self, version):
        """Return the template name for a given version"""
        return copy.deepcopy(self.config[version]['template'])


class OSTemplateView(views.MethodView):
    """OSTemplateView handles requests for OpenShift templates"""
    def __init__(self, config):
        self.config = config

    def get(self):
        """Get a rendered template as an attachment

        This route accepts query parameters to specify the template you
        would like. By default it will return the template associted with
        the `latest` key in the configuration file. The `version` query
        parameter will specify the configuration key to use for the base
        template. Any extra query parameters are passed through to the
        template for substitution. These substitutions will override any
        default parameter values.
        """
        args = flask.request.args.to_dict(flat=True)
        if len(args) == 0 or 'version' not in args:
            version = 'latest'
        else:
            version = self.config.get_version(args['version'], '404')

        if version == '404':
            resp = flask.make_response(
                    'template not found, check your parameters', 404)
        else:
            template = self.config.get_template(version)
            parameters = self.config.get_parameters(version)
            parameters.update(args)
            rend = flask.render_template(
                    template, **parameters).encode('utf-8')
            resp = flask.make_response(rend)
            resp.headers['Content-Type'] = 'text/plain'
            resp.headers['Content-Disposition'] = (
                    'attachment; filename="resources.yaml"')
        return resp


def app(config):
    """Return a configured Flask app"""
    app = flask.Flask(__name__)
    app.add_url_rule('/', view_func=OSTemplateView.as_view('index', config))
    return app


if __name__ == '__main__':
    config = ConfigWrapper()
    app = app(config)
    app.run(host='0.0.0.0', port=8080)
