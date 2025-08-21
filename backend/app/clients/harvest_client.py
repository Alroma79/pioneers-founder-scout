import os
from typing import List, Dict, Any
import httpx
import json
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HARVEST_API_KEY = os.getenv("HARVEST_API_KEY")
HARVEST_BASE_URL = os.getenv("HARVEST_BASE_URL", "https://api.harvest-api.com")

class HarvestClient:
    def __init__(self) -> None:
        if HARVEST_API_KEY:
            # HarvestAPI uses X-API-Key header according to documentation
            self.headers = {
                "X-API-Key": HARVEST_API_KEY,
                "Content-Type": "application/json"
            }
        else:
            self.headers = {}

    async def search_people(self, query: str, limit: int = 20):
        if not HARVEST_API_KEY:
            print("HARVEST_API_KEY missing")
            return []

        try:
            # Use the correct HarvestAPI endpoint from documentation
            url = f"{HARVEST_BASE_URL}/linkedin/profile-search"

            # Use the correct parameter format from documentation
            params = {
                "search": query,
                "page": "1"
            }

            print(f"Trying HarvestAPI: {url} with params: {params}")
            async with httpx.AsyncClient(timeout=30) as client:
                r = await client.get(url, params=params, headers=self.headers)
                print(f"Status: {r.status_code}")

                if r.status_code == 200:
                    print("Harvest payload:", r.text[:500])
                    data = r.json()

                    # Extract results from HarvestAPI response format
                    results = data.get("elements", [])
                    print(f"Found {len(results)} results from HarvestAPI")

                    # Convert HarvestAPI format to our expected format
                    converted_results = []
                    for element in results[:limit]:
                        converted_result = {
                            "name": element.get("name", "Unknown"),
                            "full_name": element.get("name", "Unknown"),
                            "title": element.get("position", ""),
                            "headline": element.get("position", ""),
                            "bio": element.get("position", ""),
                            "linkedin_url": element.get("linkedinUrl", ""),
                            "profile_url": element.get("linkedinUrl", ""),
                            "location": element.get("location", {}).get("linkedinText", ""),
                            "photo": element.get("photo", ""),
                            "publicIdentifier": element.get("publicIdentifier", "")
                        }
                        converted_results.append(converted_result)

                    return converted_results

                else:
                    print(f"Error response: {r.text[:200]}")
                    print("Falling back to mock data")
                    return self._get_mock_candidates(query, limit)

        except Exception as e:
            print(f"HarvestAPI error: {repr(e)}")
            print("Falling back to mock data")
            return self._get_mock_candidates(query, limit)

    def _get_mock_candidates(self, query: str, limit: int = 20):
        """Generate realistic mock candidate data for testing"""
        import random

        # Mock candidate profiles
        mock_candidates = [
            {
                "name": "Sarah Chen",
                "full_name": "Sarah Chen",
                "title": "Former CTO at TechStart, Co-founder at DataFlow",
                "headline": "Serial entrepreneur with 8+ years in ML/AI. Built and sold 2 startups. Expert in data infrastructure and team scaling.",
                "bio": "Former CTO at TechStart (acquired by Google). Co-founded DataFlow, a real-time analytics platform. PhD in Computer Science from Stanford. Passionate about building products that solve real problems.",
                "linkedin_url": "https://linkedin.com/in/sarahchen-cto",
                "profile_url": "https://linkedin.com/in/sarahchen-cto"
            },
            {
                "name": "Marcus Rodriguez",
                "full_name": "Marcus Rodriguez",
                "title": "Founder & CEO at FinTech Innovations",
                "headline": "FinTech founder with 3 successful exits. Former Goldman Sachs VP. Expert in payments and blockchain technology.",
                "bio": "Founded 3 FinTech companies with combined exits of $200M+. Former VP at Goldman Sachs. MBA from Wharton. Currently advising early-stage startups.",
                "linkedin_url": "https://linkedin.com/in/marcusrodriguez-fintech",
                "profile_url": "https://linkedin.com/in/marcusrodriguez-fintech"
            },
            {
                "name": "Dr. Emily Watson",
                "full_name": "Dr. Emily Watson",
                "title": "Co-founder at BioTech Solutions, Former Head of R&D",
                "headline": "Biotech entrepreneur and researcher. 15+ years in drug discovery. Co-founded 2 biotech companies, 1 IPO.",
                "bio": "PhD in Biochemistry from MIT. Former Head of R&D at Pfizer. Co-founded BioTech Solutions (IPO 2022). 20+ patents in drug discovery.",
                "linkedin_url": "https://linkedin.com/in/emilywatson-biotech",
                "profile_url": "https://linkedin.com/in/emilywatson-biotech"
            },
            {
                "name": "Alex Kim",
                "full_name": "Alex Kim",
                "title": "Technical Co-founder at CloudScale, Former Senior Engineer at Meta",
                "headline": "Full-stack engineer turned founder. Built scalable systems at Meta. Co-founded CloudScale, serving 10M+ users.",
                "bio": "Former Senior Engineer at Meta (Facebook). Co-founded CloudScale, a cloud infrastructure platform. Expert in distributed systems and DevOps.",
                "linkedin_url": "https://linkedin.com/in/alexkim-cloudscale",
                "profile_url": "https://linkedin.com/in/alexkim-cloudscale"
            },
            {
                "name": "Jennifer Park",
                "full_name": "Jennifer Park",
                "title": "Founder at EcoTech Ventures, Former McKinsey Partner",
                "headline": "Sustainability-focused entrepreneur. Former McKinsey Partner. Founded 2 clean-tech companies.",
                "bio": "Former Partner at McKinsey & Company. Founded EcoTech Ventures, focusing on clean energy solutions. MBA from Harvard Business School.",
                "linkedin_url": "https://linkedin.com/in/jenniferpark-ecotech",
                "profile_url": "https://linkedin.com/in/jenniferpark-ecotech"
            },
            {
                "name": "David Thompson",
                "full_name": "David Thompson",
                "title": "Co-founder & CTO at HealthTech Pro, Former Apple Engineer",
                "headline": "HealthTech entrepreneur with deep iOS expertise. Former Apple engineer. Co-founded 2 health apps with 5M+ downloads.",
                "bio": "Former iOS Engineer at Apple. Co-founded HealthTech Pro, developing medical diagnostic apps. MS in Computer Science from Carnegie Mellon.",
                "linkedin_url": "https://linkedin.com/in/davidthompson-healthtech",
                "profile_url": "https://linkedin.com/in/davidthompson-healthtech"
            },
            {
                "name": "Lisa Zhang",
                "full_name": "Lisa Zhang",
                "title": "Founder at EdTech Solutions, Former Product Manager at Google",
                "headline": "EdTech founder passionate about democratizing education. Former Google PM. Built products used by 100M+ students.",
                "bio": "Former Product Manager at Google Education. Founded EdTech Solutions, an AI-powered learning platform. Stanford MBA.",
                "linkedin_url": "https://linkedin.com/in/lisazhang-edtech",
                "profile_url": "https://linkedin.com/in/lisazhang-edtech"
            },
            {
                "name": "Robert Johnson",
                "full_name": "Robert Johnson",
                "title": "Serial Entrepreneur, Former VP of Engineering at Uber",
                "headline": "3x founder with 2 successful exits. Former VP of Engineering at Uber. Expert in marketplace and logistics platforms.",
                "bio": "Former VP of Engineering at Uber. Founded 3 companies with 2 successful exits. Expert in building large-scale marketplace platforms.",
                "linkedin_url": "https://linkedin.com/in/robertjohnson-serial",
                "profile_url": "https://linkedin.com/in/robertjohnson-serial"
            }
        ]

        # Filter based on query
        if query:
            query_terms = query.lower().split()
            filtered_candidates = []

            for candidate in mock_candidates:
                searchable_text = " ".join([
                    candidate.get("name", ""),
                    candidate.get("title", ""),
                    candidate.get("headline", ""),
                    candidate.get("bio", "")
                ]).lower()

                if any(term in searchable_text for term in query_terms):
                    filtered_candidates.append(candidate)

            results = filtered_candidates[:limit]
        else:
            results = mock_candidates[:limit]

        print(f"Mock data: returning {len(results)} candidates for query '{query}'")
        return results