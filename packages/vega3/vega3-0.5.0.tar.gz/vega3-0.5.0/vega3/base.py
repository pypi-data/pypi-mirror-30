from __future__ import absolute_import

import json
import uuid
import copy

from IPython.display import display, publish_display_data

from . import utils


class VegaBase(object):
    """A custom Vega-Lite display object."""

    DEFAULTS = {}
    JS_TEMPLATE = "static/vega.js"
    HTML_TEMPLATE = "static/vega.html"
    render_type = ''  # vega or vega-lite

    def __init__(self, spec, data=None):
        """Initialize the visualization object."""
        spec = utils.nested_update(copy.deepcopy(self.DEFAULTS), spec)
        self.spec = self._prepare_spec(spec, data)

    def _prepare_spec(self, spec, data):
        return spec

    def _generate_html(self, id):
        template = utils.get_content(self.HTML_TEMPLATE)
        return template.format(id=id)

    def _generate_js(self, id, **kwds):
        template = utils.get_content(self.JS_TEMPLATE)
        selector = '#{0}'.format(id)
        payload = template.format(
            selector=selector,
            spec=json.dumps(self.spec, **kwds),
            type=self.render_type
        )
        return payload

    def _ipython_display_(self):
        """Display the visualization in the Jupyter notebook."""
        id = uuid.uuid4()
        publish_display_data(
            {'text/html': self._generate_html(id)},
            metadata={'jupyter-vega3': '#{0}'.format(id)}
        )
        publish_display_data(
            {'application/javascript': self._generate_js(id)},
            metadata={'jupyter-vega3': '#{0}'.format(id)}
        )

    def display(self):
        """Render the visualization."""
        display(self)
