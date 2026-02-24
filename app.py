"""
Main Flask application
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from query_builder import QueryBuilder
from search_engine import SearchEngine
from name_extractor import NameExtractor
from validator import Validator

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize components
query_builder = QueryBuilder()
search_engine = SearchEngine()
name_extractor = NameExtractor()
validator = Validator()

@app.route('/search', methods=['POST'])
def search():
    """Main search endpoint"""
    try:
        data = request.json
        company = data.get('company', '').strip()
        designation = data.get('designation', '').strip()
        
        if not company or not designation:
            return jsonify({
                'error': 'Company and designation are required'
            }), 400
        
        logger.info(f"Searching for {designation} at {company}")
        
        # Step 1: Build queries
        queries = query_builder.build_queries(company, designation)
        logger.info(f"Generated {len(queries)} queries: {queries}")
        
        # Step 2: Search
        all_results = []
        for query in queries:
            logger.info(f"Executing query: {query}")
            results = search_engine.search(query, max_results=5)
            logger.info(f"Got {len(results)} raw results")
            
            filtered = search_engine.filter_credible_sources(results)
            logger.info(f"Filtered to {len(filtered)} results")
            
            all_results.extend(filtered)
        
        logger.info(f"Total results after all queries: {len(all_results)}")
        
        # Step 3: Extract names
        candidates = name_extractor.extract_names(all_results, company, designation)
        logger.info(f"Found {len(candidates)} candidates: {[c['name'] for c in candidates]}")
        
        # Step 4: Validate and calculate confidence
        best_match = validator.cross_validate(candidates, company, designation)
        
        if best_match:
            logger.info(f"Best match: {best_match['name']} with confidence {best_match['confidence']}")
            
            # Split name
            first_name, last_name = validator.split_name(best_match['name'])
            
            # Prepare response
            response = {
                'success': True,
                'person': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'current_title': designation,
                    'source_url': best_match.get('source_url', ''),
                    'confidence': round(best_match['confidence'], 2)
                },
                'sources_used': 1,
                'all_sources': [best_match.get('source_url', '')]
            }
        else:
            logger.warning("No person found matching the criteria")
            response = {
                'success': False,
                'error': 'No person found matching the criteria',
                'suggestions': 'Try broader search terms or check company spelling'
            }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in search: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/debug-search', methods=['POST'])
def debug_search():
    """Debug endpoint to see raw search results"""
    try:
        data = request.json
        company = data.get('company', '').strip()
        designation = data.get('designation', '').strip()
        
        # Build queries
        queries = query_builder.build_queries(company, designation)
        
        # Get raw results from first query only
        if queries:
            results = search_engine.search(queries[0], max_results=10)
            filtered = search_engine.filter_credible_sources(results)
            
            return jsonify({
                'query': queries[0],
                'raw_results': results[:5],
                'filtered_results': filtered[:5]
            })
        
        return jsonify({'error': 'No queries generated'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)