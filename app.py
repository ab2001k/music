from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
# Enable CORS so your HTML file can talk to this local server
CORS(app)

@app.route('/api/search', methods=['GET'])
def search_song():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"success": False, "message": "No query provided"}), 400

    # SIMULATION: This is where you would normally put your data-fetching logic.
    # We use time.sleep to simulate the time it takes to process a request (so you can see your UI spinner).
    time.sleep(2) 

    # Mock response format simulating a successful retrieval
    mock_response = {
        "success": True,
        "title": f"Result for: {query.title()}",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" # Safe, royalty-free sample
    }
    
    return jsonify(mock_response)

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)