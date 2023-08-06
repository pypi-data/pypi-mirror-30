import unittest
from uk_postcode_validator.client import PostCodeClient, ValidationError


class PostCodeTest(unittest.TestCase):
    def test_invalid_postcode_validation_fails(self):
        client = PostCodeClient()
        with self.assertRaises(ValidationError) as e:
            client.validate('695001')

    def test_valid_postcode_is_success(self):
        client = PostCodeClient()
        response = client.validate('M1 1AE')
        self.assertEqual(response, 'M1 1AE')

    def test_case_insensitive_validation_is_success(self):
        client = PostCodeClient()
        response = client.validate('ox495nu')
        self.assertEqual(response, 'OX49 5NU')

    def test_formatting_invalid_postcode_fails(self):
        client = PostCodeClient()
        with self.assertRaises(ValidationError) as e:
            client.format_code('695001')

    def test_formatting_valid_postcode_is_success(self):
        client = PostCodeClient()
        response = client.format_code('OX495NU')
        self.assertEqual(response, 'OX49 5NU')

if __name__ == '__main__':
    unittest.main()
