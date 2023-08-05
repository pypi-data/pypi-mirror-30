# -*- coding: utf-8 -*-
#
# Copyright 2016 - 2018, Ternaris and the MARV contributors.
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, division, print_function

import base64
import os

import flask
from pkg_resources import resource_filename

from marv_webapi.tooling import api_group as marv_api_group


@marv_api_group()
def frontend(app):
    site = app.site
    customdir = os.path.join(site.config.marv.frontenddir, 'custom')
    @app.route('/custom/<path:path>')
    def custom(path):
        return flask.send_from_directory(customdir, path, conditional=True)

    app_root = app.config['APPLICATION_ROOT']
    static = os.path.join(resource_filename('marv_ludwig', 'static'))
    with open(os.path.join(static, 'index.html')) as f:
        index_html = f.read().replace('MARV_APP_ROOT', app_root or "")

    customjs = os.path.join(site.config.marv.frontenddir, 'custom.js')
    try:
        with(open(customjs)) as f:
            data = base64.b64encode(f.read())
    except IOError:
        pass
    else:
        assert '<script async src="main-built.js"></script>' in index_html
        index_html = index_html.replace(
            '<script async src="main-built.js"></script>',
            '<script src="data:text/javascript;base64,{}"></script>'.format(data) +
            '\n<script async src="main-built.js"></script>', 1
        )

    customcss = os.path.join(site.config.marv.frontenddir, 'custom.css')
    try:
        with(open(customcss)) as f:
            data = base64.b64encode(f.read())
    except IOError:
        pass
    else:
        assert '<link async rel="stylesheet" href="main-built.css" />' in index_html
        index_html = index_html.replace(
            '<link async rel="stylesheet" href="main-built.css" />',
            '<link async rel="stylesheet" href="main-built.css" />' +
            '<link rel="stylesheet" href="data:text/css;base64,{}" />'.format(data), 1
        )

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def assets(path):
        if not path:
            path = 'index.html'

        if path == 'index.html':
            return index_html

        return flask.send_from_directory(static, path, conditional=True)
