# -*- coding: utf-8 -*-
"""This module contains all views for the main blueprint.

.. module:: views
    :platform: Unix
    :synopsis: Views for the main blueprint.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import tempfile
import uuid
import tarfile
from collections import defaultdict
from flask import render_template, send_file, session
from werkzeug import secure_filename
from pdfebc_core import compress
from . import main
from .forms import FileUploadForm, CompressFilesForm

PDFEBC_CORE_GITHUB = 'https://github.com/slarse/pdfebc-core'
PDFEBC_WEB_GITHUB = 'https://github.com/slarse/pdfebc-web'
UPLOADED_FILES_KEY = 'uploaded_files'
UPLOAD_DIR_KEY = 'temp_dir'
TEMPORARY_DIRECTORY = tempfile.gettempdir()
SESSION_ID_KEY = 'session_id'
UPLOAD_DIR_SUFFIX = 'pdfebc-web'
UPLOADED_FILES = defaultdict(list)

def make_tarfile(source_dir, out):
    if not out.endswith('.tgz'):
        out += '.tgz'
    with tarfile.open(out, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def compress_and_serve_uploaded_files():
    session_id = session[SESSION_ID_KEY]
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename, file_contents in UPLOADED_FILES[session_id]:
            src_file = open(os.path.join(tmpdir, filename), 'wb')
            src_file.write(file_contents)
            src_file.close()
        with tempfile.TemporaryDirectory() as tmp_out_dir:
            compress.compress_multiple_pdfs(tmpdir, tmp_out_dir, 'gs')
            out = os.path.join(tmp_out_dir, 'compressed_files.tgz')
            make_tarfile(tmp_out_dir, out)
            UPLOADED_FILES[session_id] = []
            return send_file(out)


@main.route('/', methods=['GET', 'POST'])
def index():
    """View for the index page."""
    test_form = CompressFilesForm()
    form = FileUploadForm()
    if SESSION_ID_KEY not in session:
        session[SESSION_ID_KEY] = uuid.uuid4()
    session_id = session[SESSION_ID_KEY]
    if form.validate_on_submit():
        file = form.upload.data
        UPLOADED_FILES[session_id].append((secure_filename(file.filename), file.read()))
    if test_form.validate_on_submit():
        return compress_and_serve_uploaded_files()
    return render_template('index.html', form=form,
                           uploaded_files=[file[0] for file in UPLOADED_FILES[session_id]],
                           test_form=test_form)

@main.route('/about')
def about():
    """View for the about page."""
    return render_template('about.html',
                           pdfebc_web_github=PDFEBC_WEB_GITHUB,
                           pdfebc_core_github=PDFEBC_CORE_GITHUB)
