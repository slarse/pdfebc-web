# -*- coding: utf-8 -*-
"""This module contains all views for the main blueprint.

.. module:: views
    :platform: Unix
    :synopsis: Views for the main blueprint.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import shutil
import tempfile
import uuid
import tarfile
from pdfebc_core import email_utils, compress, config_utils
from flask import render_template, session, flash, Blueprint, redirect, url_for
from werkzeug import secure_filename
from .forms import FileUploadForm, CompressFilesForm

PDFEBC_CORE_GITHUB = 'https://github.com/slarse/pdfebc-core'
PDFEBC_WEB_GITHUB = 'https://github.com/slarse/pdfebc-web'

FILE_CACHE = os.path.join(os.path.dirname(config_utils.CONFIG_PATH), 'pdfebc-web')
os.makedirs(FILE_CACHE, exist_ok=True)

SESSION_ID_KEY = 'session_id'


def make_tarfile(src_dir, out):
    """Make a tar archive from the src_dir.

    Args:
        src_dir (str): Path to the source directory.
        out: Path to the output file.
    Returns:
        str: Path to the tarball.
    """
    if not out.endswith('.tgz'):
        out += '.tgz'
    with tarfile.open(out, 'w:gz') as tar:
        tar.add(src_dir, arcname=os.path.basename(src_dir))


def compress_uploaded_files_to_tgz(src_dir, status_callback=None):
    """Compress the files in src_dir and place in a comrpessed tarball.

    Args:
        src_dir (str): Path to the source directory.
    Returns:
        str: Path to a tarball with the compressed files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        compress.compress_multiple_pdfs(src_dir, tmpdir, 'gs', status_callback=status_callback)
        out = os.path.join(src_dir, 'compressed_files.tgz')
        make_tarfile(tmpdir, out)
    return out


def compress_uploaded_files(src_dir, status_callback=None):
    """Compress the pdf files in the given source directory and place them in a
    subdirectory.

    Args:
        src_dir (str): Path to the source directory.
    Returns:
        List[str]: Paths to the compressed files.
    """
    out_dir = os.path.join(src_dir, 'compressed_files')
    os.mkdir(out_dir)
    return compress.compress_multiple_pdfs(src_dir, out_dir, 'gs', status_callback=status_callback)


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


def delete_session_upload_dir(session_id):
    """Remove all files in the session upload directory.

    Args:
        session_id (str): Id of the session.
    """
    upload_dir = get_session_upload_dir_path(session_id)
    shutil.rmtree(upload_dir)


def tarball_in_session_upload_dir(session_id):
    """Check if there is a tarball in the session upload directory.

    Ags:
        session_id (str): Id of the session.
    """
    session_upload_dir = get_session_upload_dir_path(session_id)
    return session_upload_dir_exists(session_id) and \
            any(map(lambda filename: filename.endswith('.tgz'), os.listdir(session_upload_dir)))

def construct_blueprint(celery):
    """Construct the main blueprint.

    Args:
        celery (Celery): A Celery instance.
    Returns:
        Blueprint: A Flask Blueprint.
    """
    main = Blueprint('main', __name__)

    @celery.task
    def process_uploaded_files(session_id):
        """Compress the files uploaded to the session upload directory and send them
        by email with the preconfigured values in the pdfebc-core config.

        Also clears the session upload directory when done.

        Args:
            session_id (str): Id of the session.
        """
        session_upload_dir = get_session_upload_dir_path(session_id)
        filepaths = compress_uploaded_files(session_upload_dir)
        email_utils.send_files_preconf(filepaths)
        delete_session_upload_dir(session_id)

    @main.route('/', methods=['GET', 'POST'])
    def index():
        """View for the index page."""
        compress_form = CompressFilesForm()
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
            flash("{} was successfully uploaded!".format(filename))
        if compress_form.validate_on_submit():
            process_uploaded_files.delay(session_id)
            flash("Your files are being compressed and will be sent by email upon completion.")
            return redirect(url_for('main.index'))
        uploaded_files = [] if not os.path.isdir(session_upload_dir_path) else [
            file for file in os.listdir(session_upload_dir_path) if file.endswith('.pdf')]
        return render_template('index.html', form=form,
                               uploaded_files=uploaded_files,
                               compress_form=compress_form)

    @main.route('/about')
    def about():
        """View for the about page."""
        return render_template('about.html',
                               pdfebc_web_github=PDFEBC_WEB_GITHUB,
                               pdfebc_core_github=PDFEBC_CORE_GITHUB)

    return main
