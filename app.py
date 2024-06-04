from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)
port = int(os.getenv('PORT', 4000))

# URL for Google Autocomplete API
GOOGLE_AUTOCOMPLETE_URL = "http://suggestqueries.google.com/complete/search"

# List of characters to use for modifying the query
characters = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
]

@app.route('/suggest', methods=['GET'])
def get_suggestions():
    # Get the 'query' parameter from the request
    query = request.args.get('query')
    if not query:
        # If 'query' parameter is missing, return an error response
        return jsonify(error="Query parameter is required"), 400
    
    # Set to hold all unique suggestions
    all_suggestions = set()

    # Function to get suggestions from Google Autocomplete API
    def fetch_suggestions(modified_query):
        params = {
            'client': 'chrome',
            'q': modified_query
        }
        try:
            response = requests.get(GOOGLE_AUTOCOMPLETE_URL, params=params)
            response.raise_for_status()
            suggestions = response.json()[1]
            all_suggestions.update(suggestions)
        except requests.RequestException as e:
            # Log the error for debugging purposes
            app.logger.error(f"Error fetching suggestions for query '{modified_query}': {e}")
            # Return an error response if the request fails
            return jsonify(error=str(e)), 500
    
    # Iterate over the query string to modify it by replacing characters
    for i in range(len(query)):
        # Check if current position is the start, end, or a space
        if i == 0 or i == len(query) - 1 or query[i] == ' ':
            # For each character in the list, create a modified query
            for replacement_char in characters:
                if i == 0:
                    # Insert character at the beginning
                    modified_query = replacement_char + ' ' + query
                elif i == len(query) - 1:
                    # Append character at the end
                    modified_query = query + ' ' + replacement_char
                else:
                    # Replace space with character
                    modified_query = query[:i] + ' ' + replacement_char + ' ' + query[i+1:]
                
                # Log the modified query
                app.logger.debug(f"Modified query: {modified_query}")
                # Fetch suggestions for the modified query
                fetch_suggestions(modified_query)

    # Return the collected suggestions as a JSON response
    return jsonify(suggestions=list(all_suggestions))

if __name__ == '__main__':
    # Run the Flask application in debug mode
    app.run(port=port)
