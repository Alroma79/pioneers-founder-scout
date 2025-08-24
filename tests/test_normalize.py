import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.services.normalize import normalize_person


class TestNormalize(unittest.TestCase):
    
    def test_normalize_with_full_data(self):
        """Test normalization with complete data"""
        raw = {
            "name": "John Doe",
            "position": "CTO & Co-Founder",
            "linkedinUrl": "https://linkedin.com/in/johndoe",
            "publicIdentifier": "johndoe",
            "location": {"linkedinText": "San Francisco, CA"}
        }
        
        result = normalize_person(raw)
        
        self.assertEqual(result["name"], "John Doe")
        self.assertEqual(result["profile_type"], "technical")
        self.assertIn("CTO & Co-Founder", result["summary"])
        self.assertIn("https://linkedin.com/in/johndoe", result["contacts"])
        self.assertIn("CTO & Co-Founder", result["match_justification"])
    
    def test_normalize_linkedin_member(self):
        """Test normalization with anonymous LinkedIn member"""
        raw = {
            "publicIdentifier": "john-doe-123",
            "position": "Founder & CEO"
        }
        
        result = normalize_person(raw)
        
        self.assertEqual(result["name"], "john-doe-123")
        self.assertEqual(result["profile_type"], "business")
        self.assertEqual(result["contacts"], ["https://www.linkedin.com/in/john-doe-123"])
    
    def test_normalize_invalid_public_id(self):
        """Test normalization with invalid publicIdentifier"""
        raw = {
            "publicIdentifier": "invalid@id!",
            "position": "Engineer"
        }
        
        result = normalize_person(raw)
        
        self.assertEqual(result["contacts"], [])  # Should not create invalid URL
    
    def test_normalize_minimal_data(self):
        """Test normalization with minimal data"""
        raw = {}
        
        result = normalize_person(raw)
        
        self.assertEqual(result["name"], "LinkedIn Member")
        self.assertEqual(result["profile_type"], "business")
        self.assertIn("Experienced operator/founder", result["summary"])
        self.assertEqual(result["contacts"], [])


if __name__ == '__main__':
    unittest.main()
