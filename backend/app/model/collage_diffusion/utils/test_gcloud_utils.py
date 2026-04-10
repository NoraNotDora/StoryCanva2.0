import unittest
import os
from datetime import datetime
from gcloud_utils import upload_to_bucket, test_upload

class TestGcloudUtils(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_image.png'
        with open(self.test_file, 'wb') as f:
            f.write(b'test image data')
    
    def test_upload_to_bucket(self):
        # Test upload_to_bucket function
        blob_name = 'test_blob'
        result = upload_to_bucket(b'test data', blob_name)
        
        # Verify file exists in uploads directory
        self.assertTrue(os.path.exists(result))
        
        # Verify filename format
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        expected_filename = f"{timestamp}_{blob_name}.png"
        self.assertIn(expected_filename, result)
    
    def test_test_upload(self):
        # Test test_upload function
        result = test_upload(self.test_file)
        
        # Verify file exists in uploads directory
        self.assertTrue(os.path.exists(result))
        
        # Verify filename format
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        expected_filename = f"{timestamp}_{os.path.basename(self.test_file)}.png"
        self.assertIn(expected_filename, result)
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        
        # Clean up uploaded files
        upload_dir = './uploads'
        for file in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

if __name__ == '__main__':
    unittest.main()