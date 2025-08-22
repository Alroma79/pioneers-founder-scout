import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app.services.scoring import score_candidate


class TestScoring(unittest.TestCase):
    
    def test_score_founder_technical(self):
        """Test scoring for founder with technical background"""
        person = {
            "summary": "CTO & Co-Founder at AI startup",
            "match_justification": "Strong technical founder signals"
        }
        criteria = {"technical_signal": True, "sector": "ai"}
        
        result = score_candidate(person, criteria)
        
        # Should get points for: founder(25) + technical(25) + sector(15) + leadership(15) = 80
        self.assertEqual(result["score"], 80)
        self.assertEqual(result["tier"], "A")
    
    def test_score_business_founder(self):
        """Test scoring for business founder"""
        person = {
            "summary": "CEO & Founder of fintech startup",
            "match_justification": "Serial entrepreneur"
        }
        criteria = {"technical_signal": False, "sector": "fintech"}
        
        result = score_candidate(person, criteria)
        
        # Should get points for: founder(25) + sector(15) + leadership(15) = 55
        self.assertEqual(result["score"], 55)
        self.assertEqual(result["tier"], "C")  # Below 60 threshold
    
    def test_score_technical_lead(self):
        """Test scoring for technical lead without founder experience"""
        person = {
            "summary": "Head of Engineering with PhD in ML",
            "match_justification": "Strong technical background"
        }
        criteria = {"technical_signal": True}
        
        result = score_candidate(person, criteria)
        
        # Should get points for: technical(25) + education(10) + leadership(15) = 50
        self.assertEqual(result["score"], 50)
        self.assertEqual(result["tier"], "C")
    
    def test_score_minimal_profile(self):
        """Test scoring for minimal profile"""
        person = {
            "summary": "Professional",
            "match_justification": "Basic profile"
        }
        criteria = {}
        
        result = score_candidate(person, criteria)
        
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["tier"], "C")
    
    def test_score_bounds(self):
        """Test that scores are bounded between 0 and 100"""
        person = {
            "summary": "CTO & Co-Founder & Director & Head of AI with PhD exit experience",
            "match_justification": "All possible signals"
        }
        criteria = {"technical_signal": True, "sector": "ai"}
        
        result = score_candidate(person, criteria)
        
        self.assertLessEqual(result["score"], 100)
        self.assertGreaterEqual(result["score"], 0)


if __name__ == '__main__':
    unittest.main()
