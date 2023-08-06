"""
 # Copyright (c) 2017 Boolein Integer Indonesia, PT.
 # suryakencana 4/13/17 @author nanang.suryadi@boolein.id
 #
 # You are hereby granted a non-exclusive, worldwide, royalty-free license to
 # use, copy, modify, and distribute this software in source code or binary
 # form for use in connection with the web services and APIs provided by
 # Boolein.
 #
 # As with any software that integrates with the Boolein platform, your use
 # of this software is subject to the Boolein Developer Principles and
 # Policies [http://developers.Boolein.com/policy/]. This copyright notice
 # shall be included in all copies or substantial portions of the software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 # FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 # DEALINGS IN THE SOFTWARE
 # 
 # assets
"""
import time

from pyramid.settings import asbool
from pyramid.static import QueryStringConstantCacheBuster


def includeme(config):
    config.include('pyramid_mako')
    settings = config.registry.settings
    egg = settings.get('package', 'baka')
    armors = settings.get('armor', 'baka')
    _ext = armors.get('ext', '.html')

    if asbool(armors.get('plim', True)):
        config.include('plim.adapters.pyramid_renderer')
        config.add_plim_renderer(_ext)
    else:
        config.add_mako_renderer(_ext)

    config.add_static_view('css', '{egg}:public/css'.format(egg=egg), cache_max_age=3600)
    config.add_static_view('js', '{egg}:public/js'.format(egg=egg), cache_max_age=3600)
    config.add_static_view('fonts', '{egg}:public/fonts'.format(egg=egg), cache_max_age=3600)

    config.add_static_view(armors.get('url', 'static'),
                           '{egg}:public'.format(egg=egg),
                           cache_max_age=3600)
    config.add_cache_buster('public', QueryStringConstantCacheBuster(
        str(int(time.time()))))
