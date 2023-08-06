import functools

import pkg_resources
import jinja2

from . import __name__ as module_name


j2env = jinja2.Environment(loader=jinja2.PackageLoader(module_name, 'templates'))

resource_stream = functools.partial(pkg_resources.resource_stream, module_name)
