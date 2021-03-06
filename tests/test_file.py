"""Unit tests for util.pdfebc_web.util.file module.

Author: Simon Larsén <slarse@kth.se>
"""
import os
import tarfile
import tempfile
import uuid
from unittest import TestCase
from unittest.mock import Mock, patch
from .context import pdfebc_web
import pdfebc_core.compress

def fill_directory_with_temp_files(directory, num_files, delete=False):
    """Fill up a directory with temporary files, that by default do not delete
    themselves when they go out of scope.

    Args:
        directory (str): Path to the directory to fill.
        num_files (int): Amount of files to put in the directory.
        delete (boolean): Whether the files should be deleted when they go out of scope.
    Returns:
        List[str]: Paths to the temporary files.
    """
    return [tempfile.NamedTemporaryFile(dir=directory, delete=delete).name
            for _ in range(num_files)]


class FileTest(TestCase):
    def setUp(self):
        self.trash_can = tempfile.TemporaryDirectory()
        self.temp_source_dir = tempfile.TemporaryDirectory(dir=self.trash_can.name)
        self.temp_source_dir_contents = fill_directory_with_temp_files(self.temp_source_dir.name, 20)
        pdfebc_web.util.file.FILE_CACHE = self.trash_can.name

    def test_make_tarfile_tgz_out(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_name = 'blabla.tgz'
            out = os.path.join(tmpdir, tar_name)
            pdfebc_web.util.file.make_tarfile(self.temp_source_dir.name, out)
            tmpdir_contents = os.listdir(tmpdir)
            self.assertEqual(1, len(tmpdir_contents))
            self.assertEqual(tar_name, tmpdir_contents.pop())
            self.assertTrue(tarfile.is_tarfile(out))
            with tarfile.open(out, 'r') as tar:
                contents = set(map(os.path.basename, tar.getnames()))
                expected_contents = set(map(os.path.basename, self.temp_source_dir_contents))
                source_dir_name = os.path.basename(self.temp_source_dir.name)
                self.assertTrue(source_dir_name in contents)
                self.assertTrue(expected_contents <= contents)
                self.assertEqual(len(expected_contents) + 1, len(contents))

    def test_make_tarfile_non_tgz_out(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tar_name = 'blabla.bliblu'
            expected_tar_name = tar_name + '.tgz'
            out = os.path.join(tmpdir, tar_name)
            expected_out = out + '.tgz'
            pdfebc_web.util.file.make_tarfile(self.temp_source_dir.name, out)
            tmpdir_contents = os.listdir(tmpdir)
            self.assertEqual(1, len(tmpdir_contents))
            self.assertEqual(expected_tar_name, tmpdir_contents.pop())
            self.assertTrue(tarfile.is_tarfile(expected_out))
            with tarfile.open(expected_out, 'r') as tar:
                contents = set(map(os.path.basename, tar.getnames()))
                expected_contents = set(map(os.path.basename, self.temp_source_dir_contents))
                source_dir_name = os.path.basename(self.temp_source_dir.name)
                self.assertTrue(source_dir_name in contents)
                self.assertTrue(expected_contents <= contents)
                self.assertEqual(len(expected_contents) + 1, len(contents))

    def test_make_tarfile_empty_source_dir(self):
        with tempfile.TemporaryDirectory() as empty_source_dir:
            with tempfile.TemporaryDirectory() as tmpdir:
                tar_name = 'blabla.tgz'
                out = os.path.join(tmpdir, tar_name)
                with self.assertRaises(pdfebc_web.util.file.ArchivingError):
                    pdfebc_web.util.file.make_tarfile(empty_source_dir, out)

    def test_make_tarfile_source_dir_is_file(self):
        with tempfile.NamedTemporaryFile() as tmp:
            out = os.path.join(self.trash_can.name, 'badonka.tgz')
            with self.assertRaises(pdfebc_web.util.file.ArchivingError):
                pdfebc_web.util.file.make_tarfile(tmp.name, out)

    def test_make_tarfile_source_dir_doesnt_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            source_dir_path = tmpdir
        out = os.path.join(self.trash_can.name, 'badonka.tgz')
        with self.assertRaises(pdfebc_web.util.file.ArchivingError):
            pdfebc_web.util.file.make_tarfile(source_dir_path, out)

    def test_create_session_upload_dir_with_cache_dir(self):
        file_cache = self.trash_can.name
        session_id = str(uuid.uuid4())
        pdfebc_web.util.file.create_session_upload_dir(session_id)
        expected_directory_path = os.path.join(file_cache, session_id)
        self.assertTrue(os.path.isdir(expected_directory_path))

    def test_create_session_upload_dir_with_no_cache_dir(self):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as tmpdir:
            # FILE_CACHE is reset in setUp
            file_cache = tmpdir
            pdfebc_web.util.file.FILE_CACHE = file_cache
        session_id = str(uuid.uuid4())
        pdfebc_web.util.file.create_session_upload_dir(session_id)
        expected_directory_path = os.path.join(file_cache, session_id)
        self.assertTrue(os.path.isdir(expected_directory_path))

    def test_create_session_upload_dir_that_already_exists(self):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as session_upload_dir:
            session_id = os.path.basename(session_upload_dir)
            with self.assertRaises(FileExistsError):
                pdfebc_web.util.file.create_session_upload_dir(session_id)

    def test_session_upload_dir_exists(self):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as session_upload_dir:
            session_id = os.path.basename(session_upload_dir)
            self.assertTrue(pdfebc_web.util.file.session_upload_dir_exists(session_id))

    def test_session_upload_dir_exists_no_upload_dir(self):
        session_id = os.path.basename(
            tempfile.NamedTemporaryFile(dir=self.trash_can.name).name)
        self.assertFalse(pdfebc_web.util.file.session_upload_dir_exists(session_id))

    def test_delete_empty_session_upload_dir(self):
        session_upload_dir = tempfile.TemporaryDirectory(dir=self.trash_can.name)
        session_id = os.path.basename(session_upload_dir.name)
        self.assertTrue(os.path.isdir(session_upload_dir.name))
        pdfebc_web.util.file.delete_session_upload_dir(session_id)
        self.assertFalse(os.path.isdir(session_upload_dir.name))

    def test_delete_non_existing_session_upload_dir(self):
        with tempfile.TemporaryDirectory(dir=self.trash_can.name) as session_upload_dir:
            session_id = os.path.basename(session_upload_dir)
        with self.assertRaises(FileNotFoundError):
            pdfebc_web.util.file.delete_session_upload_dir(session_id)

    def test_delete_filled_session_upload_dir(self):
        session_id = os.path.basename(self.temp_source_dir.name)
        pdfebc_web.util.file.delete_session_upload_dir(session_id)
        self.assertFalse(os.path.isdir(self.temp_source_dir.name))

    def test_tarball_in_session_upload_dir(self):
        out = os.path.join(self.temp_source_dir.name, 'archive.tgz')
        with tarfile.open(out, 'w:gz'):
            pass
        session_id = os.path.basename(self.temp_source_dir.name)
        self.assertTrue(pdfebc_web.util.file.tarball_in_session_upload_dir(session_id))

    def test_no_tarball_in_session_upload_dir(self):
        session_id = os.path.basename(self.temp_source_dir.name)
        self.assertFalse(pdfebc_web.util.file.tarball_in_session_upload_dir(session_id))


    @patch('pdfebc_core.compress.compress_multiple_pdfs', autospec=True, return_value=None)
    def test_compress_uploaded_files(self, mock_compress_multiple_files):
        with tempfile.TemporaryDirectory() as src_dir:
            gs_binary = 'gs'
            mock_callback = Mock()
            pdfebc_web.util.file.compress_uploaded_files(src_dir, gs_binary, mock_callback)
            src_dir_contents = os.listdir(src_dir)
            self.assertEqual(1, len(src_dir_contents))
            self.assertTrue(os.path.isdir(src_dir))
            mock_compress_multiple_files.assert_called_once()

    def test_compress_uploaded_files_no_src_dir(self):
        with tempfile.TemporaryDirectory() as src_dir:
            pass
        with self.assertRaises(FileNotFoundError):
            gs_binary = 'gs'
            pdfebc_web.util.file.compress_uploaded_files(src_dir, gs_binary)
        
    @patch('pdfebc_web.util.file.make_tarfile')
    @patch('pdfebc_core.compress.compress_multiple_pdfs', autospec=True, return_value=None)
    def test_compress_uploaded_files_to_tgz(self, mock_compress_multiple_pdfs, mock_make_tarfile):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('tempfile.TemporaryDirectory', autospec=True) as mock_tmpdir:
                gs_binary = 'gs'
                mock_tmpdir.return_value.__enter__.return_value = tmpdir
                pdfebc_web.util.file.compress_uploaded_files_to_tgz(self.temp_source_dir.name, gs_binary)
                mock_compress_multiple_pdfs.assert_called_once_with(
                    self.temp_source_dir.name, tmpdir, gs_binary, None)

