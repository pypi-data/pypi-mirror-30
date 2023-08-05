import os
import os.path
import ujson
from notebook.base.handlers import IPythonHandler


class TemplatesHandler(IPythonHandler):
    def initialize(self, templates=None):
        self.templates = templates

    def get(self, template=None):
        self.finish(ujson.dumps(self.templates))


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    template_dirs = nb_server_app.config.get('JupyterLabTemplates', {}).get('template_dirs', [])
    template_dirs.append(os.path.join(os.path.dirname(__file__), 'templates'))

    host_pattern = '.*$'
    print('Installing jupyterlab_templates handler on path %s' % '/templates')

    templates = []
    for path in template_dirs:
        abspath = os.path.abspath(os.path.realpath(path))
        files = [f for f in os.listdir(abspath) if os.path.isfile(os.path.join(abspath, f)) and f.endswith('.ipynb')]
        for f in files:
            with open(os.path.join(abspath, f), 'r') as fp:
                content = fp.read()
            templates.append((f, abspath, content))

    print('Available templates: %s' % ','.join(t[0] for t in templates))
    web_app.add_handlers(host_pattern, [('/templates/get', TemplatesHandler, {'templates': templates})])
