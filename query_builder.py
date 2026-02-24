"""
Smart query construction with aliases and variations
"""
class QueryBuilder:
    def __init__(self):
        self.designation_aliases = {
            'ceo': ['Chief Executive Officer', 'CEO', 'Chief Executive'],
            'cmo': ['Chief Marketing Officer', 'CMO'],
            'cto': ['Chief Technology Officer', 'CTO'],
            'cfo': ['Chief Financial Officer', 'CFO'],
            'founder': ['Founder', 'Co-Founder'],
            'director': ['Director', 'Head of'],
            'manager': ['Manager', 'Senior Manager'],
            'president': ['President', 'Chairman']
        }
        
        self.query_patterns = [
            "{designation} of {company}",
            "{company} {designation}",
            "who is the {designation} of {company}",
            "{company} leadership team",
            "{company} executives",
            "{designation} {company} profile"
        ]
    
    def get_designation_variations(self, designation):
        """Get variations of a designation"""
        designation_lower = designation.lower().strip()
        
        if designation_lower in self.designation_aliases:
            return self.designation_aliases[designation_lower]
        
        return [designation]
    
    def build_queries(self, company, designation):
        """Build multiple search queries"""
        queries = []
        
        # Add direct query
        queries.append(f"{designation} of {company}")
        
        # Add "who is" query
        queries.append(f"who is the {designation} of {company}")
        
        # Add company leadership query
        queries.append(f"{company} {designation} name")
        
        # Add specific queries for known companies
        if company.lower() in ['tesla', 'apple', 'google', 'microsoft']:
            queries.append(f"{company} {designation} wikipedia")
            queries.append(f"{company} official website leadership")
        
        return list(dict.fromkeys(queries))  # Remove duplicates