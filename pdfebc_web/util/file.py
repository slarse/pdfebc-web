# -*- coding: utf-8 -*-
"""This module contains functions for manipulating the file system.

.. module:: file
    :platform: Unix
    :synopsis: File system utility functions.

.. moduleauthor:: Simon Larsén <slarse@kth.se>
"""
import os
import tempfile
import tarfile
import shutil
from pdfebc_core import compress, config_utils

FILE_CACHE = os.path.join(os.path.dirname(config_utils.CONFIG_PATH), 'pdfebc-web')

class ArchivingError(Exception):
    """An error to be thrown something goes wrong when archiving a directory."""
    pass

def make_tarfile(src_dir, out):
    """Make a tar archive from the src_dir.

    Args:
        src_dir (str): Path to the source directory.
        out: Path to the output file.
    Returns:
        str: Path to the tarball.
    Raises:
        ArchivingError
    """
    if not os.path.isdir(src_dir):
        raise ArchivingError("'{}' is not a directory!".format(src_dir))
    if not os.listdir(src_dir):
        raise ArchivingError("The source directory is empty!")
    if not out.endswith('.tgz'):
        out += '.tgz'
    with tarfile.open(out, 'w:gz') as tar:
        tar.add(src_dir, arcname=os.path.basename(src_dir))


def compress_uploaded_files_to_tgz(src_dir, gs_binary, status_callback=None):
    """Compress the files in src_dir and place in a comrpessed tarball.

    Args:
        src_dir (str): Path to the source directory.
    Returns:
        str: Path to a tarball with the compressed files.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        compress.compress_multiple_pdfs(src_dir, tmpdir, gs_binary, status_callback=status_callback)
        out = os.path.join(src_dir, 'compressed_files.tgz')
        make_tarfile(tmpdir, out)
    return out


def compress_uploaded_files(src_dir, gs_binary, status_callback=None):
    """Compress the pdf files in the given source directory and place them in a
    subdirectory.

    Args:
        src_dir (str): Path to the source directory.
    Returns:
        List[str]: Paths to the compressed files.
    """
    out_dir = os.path.join(src_dir, 'compressed_files')
    os.mkdir(out_dir)
    return compress.compress_multiple_pdfs(
        src_dir, out_dir, gs_binary, status_callback=status_callback)


def create_session_upload_dir(session_id):
    """Create an upload directory for the session.

    Args:
        session_id (str): The id for the session.
    """
    directory = get_session_upload_dir_path(session_id)
    os.makedirs(directory)


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
