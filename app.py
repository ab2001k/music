from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
# Enable CORS so your HTML file can talk to this server
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_song():
    query = request.args.get('q', '')
    region = request.args.get('region', 'all')
    quality = request.args.get('quality', '320') # We receive this, though APIs handle their own quality
    
    if not query:
        return jsonify({"success": False, "message": "No query provided"}), 400

    # 1. Handle the Region Filter
    country_code = "US" # Default to global/US
    if region == "indian":
        country_code = "IN"
    elif region == "foreign":
        country_code = "GB" # UK/Global as an alternative

    # 2. Build the Search URL using the real iTunes Database
    # We ask for 5 results, but we will write logic to pick the best one
    safe_query = urllib.parse.quote(query)
    api_url = f"https://itunes.apple.com/search?term={safe_query}&media=music&entity=song&limit=5&country={country_code}"

    try:
        # 3. Fetch the data
        response = requests.get(api_url)
        data = response.json()

        # 4. Find the "Best Match"
        if data['resultCount'] > 0:
            # iTunes automatically sorts by best relevance. 
            # We grab the absolute #1 best match from the list.
            best_match = data['results'][0]
            
            song_title = best_match.get('trackName', 'Unknown Title')
            artist_name = best_match.get('artistName', 'Unknown Artist')
            audio_url = best_match.get('previewUrl', '')

            if not audio_url:
                return jsonify({"success": False, "message": "No download link available for this track."}), 404

            # 5. Send the real data back to your HTML page
            return jsonify({
                "success": True,
                "title": f"{song_title} by {artist_name}",
                "url": audio_url
            })
        else:
            return jsonify({"success": False, "message": "Song not found in database!"}), 404

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"success": False, "message": "Failed to search the database."}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
