"""
Enhanced search engine with better coverage
"""
import requests
import time
import logging
from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.results_per_query = 10  # Increased for better coverage
        self.ddgs = DDGS()
    
    def search(self, query, max_results=10):
        """Search using DuckDuckGo with multiple attempts"""
        logger.info(f"Searching for: {query}")
        
        try:
            # Try multiple search configurations
            search_attempts = [
                {'region': 'wt-wt', 'timelimit': None, 'max': max_results},  # Worldwide
                {'region': 'us-en', 'timelimit': 'y', 'max': max_results},   # US, past year
                {'region': 'uk-en', 'timelimit': None, 'max': max_results},  # UK
            ]
            
            all_results = []
            
            for attempt in search_attempts:
                try:
                    logger.info(f"Search attempt with region: {attempt['region']}")
                    
                    search_results = list(self.ddgs.text(
                        query,
                        region=attempt['region'],
                        safesearch='off',
                        timelimit=attempt['timelimit'],
                        max_results=attempt['max']
                    ))
                    
                    for result in search_results:
                        all_results.append({
                            'title': result.get('title', ''),
                            'link': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
                    
                    time.sleep(0.5)  # Be nice to the API
                    
                except Exception as e:
                    logger.debug(f"Search attempt failed: {e}")
                    continue
            
            # Remove duplicates
            unique_results = []
            seen_urls = set()
            
            for result in all_results:
                url = result.get('link', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            logger.info(f"Found {len(unique_results)} unique results")
            return unique_results[:max_results]
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    def filter_credible_sources(self, results):
        """Filter for credible sources with lower threshold"""
        if not results:
            return []
        
        credible_keywords = [
            'linkedin.com', 'crunchbase.com', 'wikipedia.org',
            'bloomberg.com', 'forbes.com', 'reuters.com',
            'businessinsider.com', 'techcrunch.com',
            '/about', '/team', '/leadership', '/executives',
            'ceo', 'founder', 'director', 'president'
        ]
        
        filtered = []
        
        for result in results:
            url = result.get('link', '').lower()
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            
            score = 0
            
            # Check for credible domains
            for keyword in credible_keywords:
                if keyword in url:
                    score += 2
                    break
            
            # Check for person-related terms
            person_terms = ['ceo', 'founder', 'director', 'president', 'executive', 'manager']
            for term in person_terms:
                if term in title or term in snippet:
                    score += 1
                    break
            
            # Check for company mention in title/snippet
            company_name = self.extract_company_from_query(result)  # We'll need to pass company
            if company_name and company_name.lower() in title or company_name.lower() in snippet:
                score += 1
            
            # Include if score is decent
            if score >= 1:
                result['relevance_score'] = score
                filtered.append(result)
        
        # Sort by relevance score
        filtered.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # If no filtered results, return top results
        if not filtered and results:
            return results[:3]
        
        return filtered[:5]
    
    def extract_company_from_query(self, result):
        """Helper to extract potential company name from result"""
        # This will be set by the calling function
        return None