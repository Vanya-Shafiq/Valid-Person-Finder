"""
Enhanced validation with better handling for smaller companies
"""
import re
from difflib import SequenceMatcher

class Validator:
    def __init__(self):
        self.known_people = {
            'tesla': {'elon musk': 1.0, 'elon': 0.9, 'musk': 0.9},
            'apple': {'tim cook': 1.0, 'tim': 0.9, 'cook': 0.9},
            'microsoft': {'satya nadella': 1.0, 'satya': 0.9, 'nadella': 0.9},
            'google': {'sundar pichai': 1.0, 'sundar': 0.9, 'pichai': 0.9},
            'amazon': {'andy jassy': 1.0, 'andy': 0.9, 'jassy': 0.9},
            'meta': {'mark zuckerberg': 1.0, 'mark': 0.9, 'zuckerberg': 0.9},
            'facebook': {'mark zuckerberg': 1.0, 'mark': 0.9, 'zuckerberg': 0.9}
        }
        
        # Common first and last names for validation
        self.common_first_names = [
            'john', 'jane', 'michael', 'sarah', 'david', 'lisa', 'robert',
            'mary', 'william', 'patricia', 'james', 'jennifer', 'charles',
            'linda', 'thomas', 'elizabeth', 'george', 'susan', 'joseph',
            'jessica', 'richard', 'karen', 'daniel', 'nancy', 'mark',
            'betty', 'donald', 'helen', 'paul', 'sandra', 'steven',
            'donna', 'andrew', 'carol', 'kenneth', 'ruth', 'joshua',
            'sharon', 'kevin', 'michelle', 'brian', 'laura', 'timothy'
        ]
        
        self.common_last_names = [
            'smith', 'johnson', 'williams', 'brown', 'jones', 'garcia',
            'miller', 'davis', 'rodriguez', 'martinez', 'wilson', 'anderson',
            'taylor', 'thomas', 'moore', 'jackson', 'martin', 'lee',
            'white', 'harris', 'clark', 'lewis', 'robinson', 'walker',
            'young', 'allen', 'king', 'wright', 'scott', 'torres',
            'nguyen', 'hill', 'flores', 'green', 'adams', 'nelson',
            'baker', 'hall', 'rivera', 'campbell', 'mitchell', 'carter'
        ]
    
    def cross_validate(self, candidates, company, designation):
        """Find the best candidate with lower threshold for smaller companies"""
        if not candidates:
            return None
        
        company_lower = company.lower()
        designation_lower = designation.lower()
        
        # First, check if we have a known person (high confidence)
        for candidate in candidates:
            name_lower = candidate['name'].lower()
            
            for known_company, people in self.known_people.items():
                if known_company in company_lower:
                    for person_name, confidence in people.items():
                        if person_name in name_lower or name_lower in person_name:
                            candidate['confidence'] = confidence
                            candidate['sources'] = [candidate]
                            return candidate
        
        # If no known person, evaluate all candidates with lower threshold
        best_candidate = None
        best_score = 0
        
        for candidate in candidates:
            score = self.calculate_confidence(candidate, company, designation)
            
            # Lower threshold for smaller companies (0.4 instead of 0.5)
            if score > best_score and score > 0.4:
                best_score = score
                candidate['confidence'] = score
                candidate['sources'] = [candidate]
                best_candidate = candidate
        
        return best_candidate
    
    def calculate_confidence(self, candidate, company, designation):
        """Calculate confidence score with better heuristics"""
        score = 0.2  # Base score (lowered)
        
        name = candidate.get('name', '')
        url = candidate.get('source_url', '').lower()
        validation = candidate.get('validation', '')
        context_score = candidate.get('context_score', 0)
        
        # Boost for known person
        if validation == 'known_person':
            score += 0.8
            return min(score, 1.0)
        
        # Use context score from extraction
        score += context_score * 0.4
        
        # Check URL credibility
        if 'linkedin.com' in url:
            score += 0.3
        elif 'wikipedia.org' in url:
            score += 0.3
        elif 'bloomberg.com' in url or 'forbes.com' in url:
            score += 0.25
        elif 'crunchbase.com' in url:
            score += 0.25
        elif company.lower() in url:
            score += 0.2
        
        # Check validation method
        if validation == 'full_page':
            score += 0.2
        elif validation == 'snippet':
            score += 0.1
        
        # Name quality checks
        name_parts = name.lower().split()
        
        # Check if name parts are common first/last names
        for part in name_parts:
            if part in self.common_first_names:
                score += 0.1
                break
        
        for part in name_parts:
            if part in self.common_last_names:
                score += 0.1
                break
        
        # Check name format
        if len(name_parts) >= 2:
            score += 0.1
            
            # Check if each part is properly capitalized (in original)
            if all(part[0].isupper() for part in name.split()):
                score += 0.1
        
        return min(score, 1.0)
    
    def split_name(self, full_name):
        """Split full name into first and last"""
        parts = full_name.split()
        
        if len(parts) == 2:
            return parts[0], parts[1]
        elif len(parts) == 3:
            # Handle middle name/initial
            return parts[0], ' '.join(parts[1:])
        else:
            return parts[0], parts[-1] if len(parts) > 1 else ''