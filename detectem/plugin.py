import re
import inspect
import logging
import glob

from importlib.util import find_spec, module_from_spec

from zope.interface import implementer, Interface, Attribute
from zope.interface.verify import verifyObject
from zope.interface.exceptions import BrokenImplementation

logger = logging.getLogger('detectem')


def get_plugin_by_name(name, plugins):
    try:
        return [p for p in plugins if p.name == name][0]
    except IndexError:
        return None


def get_plugin_module_paths(plugin_dir):
    filepaths = [
        fp for fp in glob.glob('{}/**/*.py'.format(plugin_dir), recursive=True)
        if not fp.endswith('__init__.py')
    ]

    relative_paths = [re.sub(plugin_dir.rstrip('/') + '/', '', fp) for fp in filepaths]
    module_paths = [rp.replace('/', '.').replace('.py', '') for rp in relative_paths]
    return module_paths


def load_plugins():
    """ Return the list of plugin instances """
    plugins = []
    plugins_module = 'detectem.plugins'

    # Resolve directory in the filesystem
    plugin_dir = find_spec(plugins_module).submodule_search_locations[0]
    plugin_dir = plugin_dir

    for module_path in get_plugin_module_paths(plugin_dir):
        # Load the module dynamically
        spec = find_spec('{}.{}'.format(plugins_module, module_path))
        m = module_from_spec(spec)
        spec.loader.exec_module(m)

        # Get classes from module and extract the plugin classes
        classes = inspect.getmembers(m, predicate=inspect.isclass)

        for name, klass in classes:
            if klass == Plugin:
                continue

            ins = klass()

            try:
                if verifyObject(IPlugin, ins):
                    plugins.append(ins)
            except BrokenImplementation:
                logger.warning(
                    "Plugin %(name)s doesn't meet the plugin interface",
                    {'name': name}
                )

    return plugins


class IPlugin(Interface):
    name = Attribute(""" Name to identify the plugin. """)


@implementer(IPlugin)
class Plugin():
    def _get_matchers(self, value):
        return [m[value] for m in self.matchers if value in m]

    def get_url_matchers(self):
        return self._get_matchers('url')

    def get_body_matchers(self):
        return self._get_matchers('body')

    def get_header_matchers(self):
        return self._get_matchers('header')
