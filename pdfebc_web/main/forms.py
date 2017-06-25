# -*- coding: utf-8 -*-
"""Module containing forms for use pdfebc-web.

.. module:: forms
    :platform: Unix
    :synopsis: Forms for use in pdfebc-web.
.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import SubmitField
from wtforms.validators import Required

ALLOWED_FILETYPES = set(['pdf'])

class FileUploadForm(FlaskForm):
    """A form for uploading a single PDF file."""
    upload = FileField("Upload a PDF!", validators=[
        FileAllowed(ALLOWED_FILETYPES),
        FileRequired("No file selected!")])
    submit = SubmitField("Submit", validators=[Required()])

class CompressFilesForm(FlaskForm):
    """A form for compressing uploaded files."""
    compress = SubmitField("Compress files", validators=[Required()])
