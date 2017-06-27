# -*- coding: utf-8 -*-
"""This module contains all views for the main blueprint.

.. module:: views
    :platform: Unix
    :synopsis: Views for the main blueprint.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import uuid
from pdfebc_core import email_utils, config_utils
from flask import render_template, session, flash, Blueprint, redirect, url_for
from werkzeug import secure_filename
from .forms import FileUploadForm, CompressFilesForm
from ..util.file import (create_session_upload_dir,
                         session_upload_dir_exists,
                         get_session_upload_dir_path,
                         delete_session_upload_dir,
                         compress_uploaded_files)

PDFEBC_CORE_GITHUB = 'https://github.com/slarse/pdfebc-core'
PDFEBC_WEB_GITHUB = 'https://github.com/slarse/pdfebc-web'


SESSION_ID_KEY = 'session_id'


def construct_blueprint(celery):
    """Construct the main blueprint.

    Args:
        celery (Celery): A Celery instance.
    Returns:
        Blueprint: A Flask Blueprint.
    """
    main = Blueprint('main', __name__)
    #TODO This is a suboptimal way of reading the config, fix it!
    if config_utils.valid_config_exists():
        config = config_utils.read_config()
        gs_binary = config_utils.get_attribute_from_config(config, config_utils.DEFAULT_SECTION_KEY,
                                                           config_utils.GS_DEFAULT_BINARY_KEY)
    else:
        gs_binary = 'gs'

    @celery.task
    def process_uploaded_files(session_id):
        """Compress the files uploaded to the session upload directory and send them
        by email with the preconfigured values in the pdfebc-core config.

        Also clears the session upload directory when done.

        Args:
            session_id (str): Id of the session.
        """
        session_upload_dir = get_session_upload_dir_path(session_id)
        filepaths = compress_uploaded_files(session_upload_dir, gs_binary)
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
