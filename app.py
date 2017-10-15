"""radleyberg-printing-press main app module

The Radleyberg printing press is a Flask server that transforms HTTP
requests into OpenShift templates.
"""
import flask
from flask import views
import yaml


class ConfigWrapper():
    """A helper for dealing with the configuration file"""
    def __init__(self):
        self.config = yaml.load(open('config.yaml').read())

    def has_version(self, version):
        """Does the config know about this version?"""
        return version in self.config

    def get(self, *args, **kwargs):
        return self.config.get(*args, **kwargs)

    def get_template(self, version):
        """Return the template name for a given version"""
        return self.config[version]['template']


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
        args = flask.request.args
        if len(args) == 0 or 'version' not in args:
            version = 'latest'
        else:
            version = self.config.get(args['version'], '404')

        if version == '404':
            resp = flask.make_response(
                    'template not found, check your parameters', 404)
        else:
            template = self.config.get_template(version)
            rend = flask.render_template(template, **args).encode('utf-8')
            resp = flask.make_response(rend)
            resp.headers['Content-Type'] = 'text/plain'
            resp.headers['Content-Disposition'] = (
                    'attachment; filename="resources.yaml"')
        return resp


def main():
    """start the server"""
    app = flask.Flask(__name__)
    config = ConfigWrapper()
    app.add_url_rule('/', view_func=OSTemplateView.as_view('index', config))
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
