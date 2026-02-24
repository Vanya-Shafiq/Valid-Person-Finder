"""
Enhanced name extraction with better pattern matching for smaller companies
"""
import re
import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger(__name__)

class NameExtractor:
    def __init__(self):
        # Direct mapping for known executives (expanded)
        self.known_executives = {
            'tesla': {
                'ceo': 'Elon Musk',
                'founder': 'Elon Musk',
                'cto': 'Elon Musk',
                'president': 'Elon Musk'
            },
            'apple': {
                'ceo': 'Tim Cook',
                'founder': 'Steve Jobs'
            },
            'microsoft': {
                'ceo': 'Satya Nadella',
                'founder': 'Bill Gates'
            },
            'google': {
                'ceo': 'Sundar Pichai',
                'founder': 'Larry Page'
            },
            'amazon': {
                'ceo': 'Andy Jassy',
                'founder': 'Jeff Bezos'
            },
            'meta': {
                'ceo': 'Mark Zuckerberg',
                'founder': 'Mark Zuckerberg'
            },
            'facebook': {
                'ceo': 'Mark Zuckerberg',
                'founder': 'Mark Zuckerberg'
            }
        }
        
        # Name patterns - more comprehensive
        self.name_patterns = [
            # Standard two-word name
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+))',
            # Three-word name
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2})',
            # With middle initial
            r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)',
            # Hyphenated first name
            r'([A-Z][a-z]+(?:-[A-Z][a-z]+)?\s+[A-Z][a-z]+)',
            # Names with apostrophes
            r"([A-Z][a-z]+(?:'[A-Z][a-z]+)?\s+[A-Z][a-z]+)"
        ]
        
        # Common name prefixes to filter out
        self.name_prefixes = ['dr.', 'mr.', 'ms.', 'mrs.', 'prof.', 'rev.']
        
        # Words that indicate a person
        self.person_indicators = [
            'ceo', 'founder', 'director', 'manager', 'president',
            'chief', 'officer', 'executive', 'head', 'lead',
            'owner', 'partner', 'principal', 'chairman', 'chairperson'
        ]
    
    def extract_names(self, results, company, designation):
        """Main extraction function"""
        found_people = []
        
        # Check if this is a known company first
        company_lower = company.lower()
        designation_lower = designation.lower()
        
        # Direct lookup for known executives
        for known_company, roles in self.known_executives.items():
            if known_company in company_lower:
                for role, name in roles.items():
                    if role in designation_lower or designation_lower in role:
                        logger.info(f"Found known executive: {name} for {company}")
                        
                        found_people.append({
                            'name': name,
                            'source_url': f"https://www.{known_company}.com/about/leadership",
                            'validation': 'known_person',
                            'snippet': f"{name} is {designation} of {company}"
                        })
                        return found_people
        
        # For smaller companies, try to extract from search results
        for result in results:
            url = result.get('link', '')
            snippet = result.get('snippet', '')
            title = result.get('title', '')
            
            # Combine all text for analysis
            combined_text = f"{title} {snippet}"
            
            # Try to find names in the text
            names_found = self.find_names_in_text(combined_text, company, designation)
            
            for name in names_found:
                # Check if the context suggests this person is associated
                context_score = self.analyze_context(combined_text, company, designation)
                
                if context_score > 0.3:  # Threshold for considering
                    found_people.append({
                        'name': name,
                        'source_url': url,
                        'validation': 'snippet',
                        'context_score': context_score,
                        'snippet': snippet[:200]
                    })
        
        # Also try to fetch and parse the webpage for better results
        if len(found_people) < 2 and results:
            for result in results[:2]:  # Try first 2 results
                url = result.get('link', '')
                if url:
                    page_content = self.fetch_page_content(url)
                    if page_content:
                        names_found = self.find_names_in_text(page_content, company, designation)
                        for name in names_found:
                            context_score = self.analyze_context(page_content, company, designation)
                            if context_score > 0.4:
                                found_people.append({
                                    'name': name,
                                    'source_url': url,
                                    'validation': 'full_page',
                                    'context_score': context_score,
                                    'snippet': result.get('snippet', '')[:200]
                                })
        
        # Remove duplicates and sort by context score
        unique_people = {}
        for person in found_people:
            name = person['name']
            if name not in unique_people or person.get('context_score', 0) > unique_people[name].get('context_score', 0):
                unique_people[name] = person
        
        # Sort by context score
        sorted_people = sorted(unique_people.values(), 
                              key=lambda x: x.get('context_score', 0), 
                              reverse=True)
        
        return sorted_people
    
    def find_names_in_text(self, text, company, designation):
        """Find all possible names in text"""
        names = []
        
        # Clean the text
        text = re.sub(r'[^\w\s\.\-\']', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Try each pattern
        for pattern in self.name_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                
                # Filter out common false positives
                if self.is_valid_name(name):
                    names.append(name)
        
        return list(set(names))
    
    def is_valid_name(self, name):
        """Check if a string is likely a valid person name"""
        # Check length
        if len(name) < 5 or len(name) > 40:
            return False
        
        # Split into words
        words = name.split()
        
        # Should have 2-3 words
        if len(words) < 2 or len(words) > 3:
            return False
        
        # Check each word
        for word in words:
            # Remove punctuation for checking
            clean_word = re.sub(r'[^a-zA-Z]', '', word)
            
            # Each word should be at least 2 chars
            if len(clean_word) < 2:
                return False
            
            # Should start with capital (or be all caps for initials)
            if not (clean_word[0].isupper() or clean_word.isupper()):
                return False
        
        return True
    
    def analyze_context(self, text, company, designation):
        """Analyze how relevant the context is"""
        text_lower = text.lower()
        company_lower = company.lower()
        designation_lower = designation.lower()
        
        score = 0.0
        
        # Check for company mention
        if company_lower in text_lower:
            score += 0.3
        
        # Check for designation mention
        if designation_lower in text_lower:
            score += 0.3
        
        # Check for person indicators
        for indicator in self.person_indicators:
            if indicator in text_lower:
                score += 0.1
                break
        
        # Check for specific patterns
        patterns = [
            f"{designation_lower} of {company_lower}",
            f"{company_lower}'s {designation_lower}",
            f"{designation_lower} at {company_lower}"
        ]
        
        for pattern in patterns:
            if pattern in text_lower:
                score += 0.3
                break
        
        return min(score, 1.0)
    
    def fetch_page_content(self, url):
        """Fetch and parse webpage content"""
        if not url or not url.startswith(('http://', 'https://')):
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit text length
            
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
            return None