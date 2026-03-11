from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse

app = Flask(__name__)
# Enable CORS so your HTML file can talk to this server from anywhere
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_song():
    # 1. Catch the inputs from your frontend
    query = request.args.get('q', '')
    region = request.args.get('region', 'all')
    quality = request.args.get('quality', '320') # Captured, but APIs output their max native quality
    
    if not query:
        return jsonify({"success": False, "message": "No song name provided!"}), 400

    # 2. Advanced Region Routing
    # We tell the database exactly which country's charts to prioritize
    country_code = "US" # Default to Global
    if region == "indian":
        country_code = "IN"
    elif region == "foreign":
        country_code = "GB" # UK charts for foreign/pop

    # 3. Build the secure API request
    safe_query = urllib.parse.quote(query)
    api_url = f"https://itunes.apple.com/search?term={safe_query}&media=music&entity=song&limit=3&country={country_code}"

    try:
        # Fetch data from the database
        response = requests.get(api_url, timeout=10) # Added a 10-second timeout so it doesn't hang forever
        data = response.json()

        # 4. Process the "Best Match"
        if data['resultCount'] > 0:
            # Grab the absolute #1 most relevant result
            best_match = data['results'][0]
            
            # Extract the raw data
            song_title = best_match.get('trackName', 'Unknown Title')
            artist_name = best_match.get('artistName', 'Unknown Artist')
            album_name = best_match.get('collectionName', 'Unknown Album')
            audio_url = best_match.get('previewUrl', '')
            
            # 5. The "Secret" High-Res Artwork Trick
            # Apple sends a tiny 100x100 image by default. We dynamically rewrite the URL to get a crisp 600x600 image.
            low_res_art = best_match.get('artworkUrl100', '')
            high_res_art = low_res_art.replace('100x100bb', '600x600bb') if low_res_art else ''

            # Safety check: ensure there is actually an audio file attached
            if not audio_url:
                return jsonify({"success": False, "message": "No audio file available for this specific track."}), 404

            # 6. Package it beautifully and send it back to the Face
            return jsonify({
                "success": True,
                "title": song_title,
                "artist": artist_name,
                "album": album_name,
                "cover_art": high_res_art,
                "url": audio_url
            })
        else:
            return jsonify({"success": False, "message": "Song not found in the global database!"}), 404

    except requests.exceptions.RequestException as e:
        print(f"Network Error: {e}")
        return jsonify({"success": False, "message": "Failed to connect to the music database."}), 502
    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"success": False, "message": "Internal brain error."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
