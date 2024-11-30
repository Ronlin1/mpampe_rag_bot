import unittest
from flask import Flask
from flask_testing import TestCase
from unittest.mock import patch
import app  # Assuming your main application code is in a file named app.py

class TestChatApp(TestCase):

    def create_app(self):
        app.app.config['TESTING'] = True
        return app.app

    @patch('app.get_chat_response')
    def test_chat_endpoint(self, mock_get_chat_response):
        # Mock the get_chat_response function
        mock_get_chat_response.return_value = "Mocked response"

        # Send a POST request to the /get endpoint
        response = self.client.post('/get', data={'msg': 'Test message'})

        # Check if the response is as expected
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Mocked response')

if __name__ == '__main__':
    unittest.main()
