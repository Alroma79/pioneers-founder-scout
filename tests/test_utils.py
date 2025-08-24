import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.services.utils import dedupe, candidate_key


class TestUtils(unittest.TestCase):
    
    def test_candidate_key_with_public_id(self):
        """Test candidate key generation with publicIdentifier"""
        person = {
            "publicIdentifier": "john-doe-123",
            "name": "John Doe",
            "position": "CTO"
        }
        
        key = candidate_key(person)
        
        self.assertEqual(key, ("id", "john-doe-123"))
    
    def test_candidate_key_without_public_id(self):
        """Test candidate key generation without publicIdentifier"""
        person = {
            "name": "Jane Smith",
            "position": "Founder & CEO"
        }
        
        key = candidate_key(person)
        
        self.assertEqual(key, ("jane smith", "founder & ceo"))
    
    def test_candidate_key_empty_data(self):
        """Test candidate key generation with empty data"""
        person = {}
        
        key = candidate_key(person)
        
        self.assertEqual(key, ("", ""))
    
    def test_dedupe_by_public_id(self):
        """Test deduplication using publicIdentifier"""
        candidates = [
            {"publicIdentifier": "john-doe", "name": "John Doe", "position": "CTO"},
            {"publicIdentifier": "jane-smith", "name": "Jane Smith", "position": "CEO"},
            {"publicIdentifier": "john-doe", "name": "John D.", "position": "CTO & Founder"},  # Duplicate
        ]
        
        result = dedupe(candidates)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["publicIdentifier"], "john-doe")
        self.assertEqual(result[1]["publicIdentifier"], "jane-smith")
    
    def test_dedupe_by_name_position(self):
        """Test deduplication using name and position"""
        candidates = [
            {"name": "Alice Johnson", "position": "Founder"},
            {"name": "Bob Wilson", "position": "CTO"},
            {"name": "Alice Johnson", "position": "Founder"},  # Duplicate
        ]
        
        result = dedupe(candidates)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alice Johnson")
        self.assertEqual(result[1]["name"], "Bob Wilson")
    
    def test_dedupe_mixed_keys(self):
        """Test deduplication with mixed key types"""
        candidates = [
            {"publicIdentifier": "alice-j", "name": "Alice Johnson", "position": "Founder"},
            {"name": "Bob Wilson", "position": "CTO"},  # No publicIdentifier
            {"publicIdentifier": "alice-j", "name": "Alice J.", "position": "CEO"},  # Duplicate by ID
            {"name": "Bob Wilson", "position": "CTO"},  # Duplicate by name/position
        ]
        
        result = dedupe(candidates)
        
        self.assertEqual(len(result), 2)
    
    def test_dedupe_empty_list(self):
        """Test deduplication with empty list"""
        result = dedupe([])
        
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
