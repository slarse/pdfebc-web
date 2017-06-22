# -*- coding: utf-8 -*-
"""This module contains all views for the main blueprint.

.. module:: views
    :platform: Unix
    :synopsis: Views for the main blueprint.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
from tempfile import TemporaryDirectory
from flask import render_template, send_file
from werkzeug import secure_filename
from pdfebc_core import compress
from . import main
from .forms import FileUploadForm

PDFEBC_CORE_GITHUB = 'https://github.com/slarse/pdfebc-core'
PDFEBC_WEB_GITHUB = 'https://github.com/slarse/pdfebc-web'

@main.route('/', methods=['GET', 'POST'])
def index():
    """View for the index page."""
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.upload.data
        filename = secure_filename(file.filename)
        with TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, filename)
            file.save(src)
            out = os.path.join(tmpdir, 'compressed_' + filename)
            compress.compress_pdf(src, out, 'gs')
            return send_file(out)
    return render_template('index.html', form=form)

@main.route('/about')
def about():
    """View for the about page."""
    return render_template('about.html',
                           pdfebc_web_github=PDFEBC_WEB_GITHUB,
                           pdfebc_core_github=PDFEBC_CORE_GITHUB)
