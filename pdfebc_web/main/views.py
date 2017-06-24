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
from flask import render_template, send_file, session, flash
from werkzeug import secure_filename
from pdfebc_core import compress
from . import main
from .forms import FileUploadForm, CompressFilesForm

PDFEBC_CORE_GITHUB = 'https://github.com/slarse/pdfebc-core'
PDFEBC_WEB_GITHUB = 'https://github.com/slarse/pdfebc-web'

FILE_CACHE = os.path.join(tempfile.gettempdir(), 'pdfebc-web')
os.makedirs(FILE_CACHE, exist_ok=True)

SESSION_ID_KEY = 'session_id'

def make_tarfile(source_dir, out):
    if not out.endswith('.tgz'):
        out += '.tgz'
    with tarfile.open(out, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def compress_uploaded_files(src_dir):
    """Compress the files in src_dir and place in an archive.

    Args:
        src_dir (str): Path to the source directory.
    Returns:
        str: Path to a tarball with the compressed files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        compress.compress_multiple_pdfs(src_dir, tmpdir, 'gs')
        out = os.path.join(src_dir, 'compressed_files.tgz')
        make_tarfile(tmpdir, out)
    return out


def create_session_upload_dir(session_id):
    """Create an upload directory for the session.

    Args:
        session_id (str): The id for the session.
    """
    directory = get_session_upload_dir_path(session_id)
    os.mkdir(directory)


def get_session_upload_dir_path(session_id):
    """Return the path to the session upload directory

    Args:
        session_id (str): The id for the session.
    """
    return os.path.join(FILE_CACHE, session_id)


def session_upload_dir_exists(session_id):
    """Check if the session upload directory exists.

    Args:
        session_id (str): The id for the session.
    """
    directory = get_session_upload_dir_path(session_id)
    return os.path.isdir(directory)


@main.route('/', methods=['GET', 'POST'])
def index():
    """View for the index page."""
    test_form = CompressFilesForm()
    form = FileUploadForm()
    if SESSION_ID_KEY not in session:
        session[SESSION_ID_KEY] = str(uuid.uuid4())
    session_id = session[SESSION_ID_KEY]
    session_upload_dir_path = get_session_upload_dir_path(session_id)
    if not session_upload_dir_exists(session_id):
        create_session_upload_dir(session_id)
    if form.validate_on_submit():
        file = form.upload.data
        filename = secure_filename(file.filename)
        file.save(
            os.path.join(session_upload_dir_path, filename))
        flash("File {} was uploaded!".format(filename))
    if test_form.validate_on_submit():
        tar = compress_uploaded_files(session_upload_dir_path)
        return send_file(tar, as_attachment=True)
    return render_template('index.html', form=form,
                           uploaded_files=[file for file in os.listdir(session_upload_dir_path)],
                           test_form=test_form)

@main.route('/about')
def about():
    """View for the about page."""
    return render_template('about.html',
                           pdfebc_web_github=PDFEBC_WEB_GITHUB,
                           pdfebc_core_github=PDFEBC_CORE_GITHUB)
