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
    # limit=3 tells the database we want the top 3 results
    api_url = f"https://itunes.apple.com/search?term={safe_query}&media=music&entity=song&limit=3&country={country_code}"

    try:
        # Fetch data from the database
        response = requests.get(api_url, timeout=10) # Added a 10-second timeout so it doesn't hang forever
        data = response.json()

        # 4. Process the Top Matches
        if data.get('resultCount', 0) > 0:
            top_tracks = []
            
            # Loop through the results (up to 3)
            for item in data['results']:
                audio_url = item.get('previewUrl', '')
                
                # Safety check: only add the track if there is actually an audio file attached
                if audio_url:
                    # The "Secret" High-Res Artwork Trick
                    low_res_art = item.get('artworkUrl100', '')
                    high_res_art = low_res_art.replace('100x100bb', '600x600bb') if low_res_art else ''
                    
                    # Package this specific track
                    track_info = {
                        "title": item.get('trackName', 'Unknown Title'),
                        "artist": item.get('artistName', 'Unknown Artist'),
                        "album": item.get('collectionName', 'Unknown Album'),
                        "cover_art": high_res_art,
                        "url": audio_url
                    }
                    top_tracks.append(track_info)
            
            # If we filtered out broken tracks and ended up with nothing
            if not top_tracks:
                return jsonify({"success": False, "message": "No playable audio found for this search."}), 404

            # 5. Send the ARRAY back to the Face
            return jsonify({
                "success": True,
                "results": top_tracks
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
