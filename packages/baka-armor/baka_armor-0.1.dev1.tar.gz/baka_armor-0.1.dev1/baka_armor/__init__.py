"""
 # Copyright (c) 06 2016 | suryakencana
 # 6/13/16 nanang.ask@kubuskotak.com
 # This program is free software; you can redistribute it and/or
 # modify it under the terms of the GNU General Public License
 # as published by the Free Software Foundation; either version 2
 # of the License, or (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 #  __init__.py
"""

import fileinput
import logging
import os
from contextlib import closing
from os import path

import six
from pyramid.path import AssetResolver
from pyramid.settings import asbool
from webassets import Bundle
from webassets.env import Environment, Resolver
from webassets.exceptions import BundleError
from webassets.loaders import YAMLLoader

from baka_armor.config import CONFIG
from baka_armor.ui import _split_spec

__version__ = '0.1.dev1'

LOG = logging.getLogger(__name__)


# fork from https://github.com/sontek/pyramid_webassets/blob/master/pyramid_webassets/__init__.py
class PyramidResolver(Resolver):
    def __init__(self):
        super(PyramidResolver, self).__init__()
        self.resolver = AssetResolver(None)

    def _split_spec(self, item):
        if ':' in item:
            package, subpath = item.split(':', 1)
            return package, subpath
        else:
            return None, item

    def _resolve_spec(self, spec):
        package, subpath = self._split_spec(spec)

        try:
            pkgpath = self.resolver.resolve(package + ':').abspath()
        except ImportError as e:
            raise BundleError(e)
        else:
            return path.join(pkgpath, subpath)

    def search_for_source(self, ctx, item):
        package, subpath = self._split_spec(item)
        if package is None:
            return super(PyramidResolver, self).search_for_source(
                ctx,
                item
            )
        else:
            pkgpath = self._resolve_spec(package + ':')
            return self.consider_single_directory(pkgpath, subpath)

    def resolve_output_to_path(self, ctx, target, bundle):
        package, filepath = self._split_spec(target)
        if package is not None:
            pkgpath = self._resolve_spec(package + ':')
            target = path.join(pkgpath, filepath)

        return super(PyramidResolver, self).resolve_output_to_path(
            ctx,
            target,
            bundle
        )


class Environment(Environment):
    @property
    def resolver_class(self):
        return PyramidResolver


def includeme(config):
    """pyramid include. declare the add_thumb_view"""
    # inject config schema for validity then find and add value from config.yaml

    # get setting values
    settings = config.get_settings()
    egg = settings.get('package', 'baka')
    # spesial untuk validator schema config
    if settings.get('validator', False):
        config.add_config_validator(CONFIG)
    config.get_settings_validator()
    armors = settings.get('armor', {})
    config.include('.assets')
    config.include('.ui')

    def _path_setting(path):
        package, subpath = _split_spec(path)
        if package is None:
            path = '{egg}:{static}'.format(static=subpath, egg=egg)
        else:
            path = '{egg}:{static}'.format(static=subpath, egg=package)
        return path

    config_dir = _path_setting(armors.get('config'))
    asset_dir = _path_setting(armors.get('assets'))

    isabs_config = os.path.isabs(config_dir)
    if (not isabs_config) and (':' in config_dir):
        pkg, relto = config_dir.split(':')
        config_dir = AssetResolver(pkg).resolve(relto).abspath()

    isabs_asset = os.path.isabs(asset_dir)
    if (not isabs_asset) and (':' in asset_dir):
        pkg, relto = asset_dir.split(':')
        asset_dir = AssetResolver(pkg).resolve(relto).abspath()

    # asset_dir = AssetResolver(None).resolve(asset_dir).abspath()

    env = Environment(
        directory=asset_dir,
        url=armors.get('url', 'static'))
    env.manifest = armors.get('manifest', 'file')
    env.debug = asbool(armors.get('debug', False))
    env.cache = asbool(armors.get('cache', False))
    env.auto_build = asbool(armors.get('auto_build', True))

    def text(value):
        if type(value) is six.binary_type:
            return value.decode('utf-8')
        else:
            return value

    def yaml_stream(fname, mode):
        if path.exists(fname):
            return open(fname, mode)
        else:
            return open(AssetResolver().resolve(fname).abspath(), mode)

    LOG.debug(AssetResolver().resolve(
        '/'.join([
            config_dir,
            armors.get('bundles', 'assets.yaml')])).abspath())

    fin = fileinput.input('/'.join([
        config_dir,
        armors.get('bundles', 'assets.yaml')]),
        openhook=yaml_stream)
    with closing(fin):
        lines = [text(line).rstrip() for line in fin]
    stream_yaml = six.StringIO('\n'.join(lines))
    loader = YAMLLoader(stream_yaml)
    result = loader.load_bundles()
    env.register(result)

    # for item in env:
    #     LOG.debug(item.output)
    #     path_file = '/'.join([public_dir, item.output])
    #     src_file = '/'.join([asset_dir, item.output])
    #     shutil.copy(src_file, path_file)

    def _get_assets(request, *args, **kwargs):
        bundle = Bundle(*args, **kwargs)
        with bundle.bind(env):
            urls = bundle.urls()
        return urls
    config.add_request_method(_get_assets, 'web_assets')

    def _add_assets_global(event):
        event['web_env'] = env

    config.add_subscriber(_add_assets_global, 'pyramid.events.BeforeRender')

    def _get_assets_env(request):
        return env
    config.add_request_method(_get_assets_env, 'web_env', reify=True)

