import unittest
import os
import pandas as pd
import tempfile
import shutil
import polars as pl
import openpyxl
from unittest.mock import patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from File_handler import FileHandler

class TestFileHandler(unittest.TestCase):
    @patch('polars.read_excel')
    def setUp(self, mock_read_excel):
        # Mocking read_excel to return test data
        mock_data = pl.DataFrame({
            "BRnum": ["123", "456"],
            "Pdf_URL": ["http://example.com/file1.pdf", None],
            "Report Html Address": [None, "http://example.com/file2.html"]
        })
        mock_read_excel.return_value = mock_data
        
        # Create a temporary Excel file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            self.file_path_gri = temp_file.name
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # Adding headers and sample data
        sheet.append(["BRnum", "Pdf_URL", "Report Html Address"])
        sheet.append(["123", "http://example.com/file1.pdf", None])
        sheet.append(["456", None, "http://example.com/file2.html"])
        workbook.save(self.file_path_gri)
        
        # Create temporary folders for destination and output
        self.destination_folder = tempfile.mkdtemp()
        self.output_folder = tempfile.mkdtemp()

        # Create a FileHandler instance
        self.file_handler = FileHandler(self.file_path_gri, self.destination_folder, self.output_folder)

    @patch('Downloader.Downloader.download', return_value=True)
    def test_start_download(self, mock_download):
        # Mock the download method to simulate both success and failure
        mock_download.side_effect = [True, False]  # First download succeeds, second fails

        # Run the download process
        self.file_handler.start_download()

        # Assert that the download method was called twice
        self.assertEqual(mock_download.call_count, 2)

    @patch('pandas.DataFrame.to_excel')
    def test_write_downloaded_files(self, mock_to_excel):
        # Prepare a sample log list to simulate writing logs to an Excel file
        log_list = [
            {"BRNum": "123", "Download_Status": "Downloadet"},
            {"BRNum": "456", "Download_Status": "Ikke downloadet"}
        ]

        # Call the write_downloaded_files method
        self.file_handler.write_downloaded_files(log_list)

        # Assert that the to_excel method was called exactly once
        mock_to_excel.assert_called_once()

    def tearDown(self):
        # Clean up created files and folders
        os.remove(self.file_path_gri)  # Remove the temporary Excel file
        shutil.rmtree(self.destination_folder, ignore_errors=True)  # Remove the destination folder
        shutil.rmtree(self.output_folder, ignore_errors=True)  # Remove the output folder

if __name__ == '__main__':
    unittest.main()
