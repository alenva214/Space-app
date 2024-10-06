from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import os
from utils.landsat_api import LandsatAPI
from utils.data_processing import process_landsat_data, create_csv
from database import init_app, db, User, Search, save_search, save_pixel_data
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
init_app(app)

landsat_api = LandsatAPI(
    username=app.config['LANDSAT_USERNAME'],
    password=app.config['LANDSAT_PASSWORD']
)

# Update the route handlers to use the database functions
@app.route('/api/landsat/data', methods=['POST'])
def get_landsat_data():
    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    scene_id = data.get('scene_id')
    
    try:
        pixel_data = landsat_api.get_pixel_data(scene_id, lat, lon)
        processed_data = process_landsat_data(pixel_data)
        
        # Save to database - assuming user_id 1 for now
        search = save_search(user_id=1, lat=lat, lon=lon, 
                            scene_id=scene_id, 
                            cloud_cover=processed_data.get('metadata', {}).get('cloud_cover'))
        
        # Save pixel data
        for i, pixel in enumerate(processed_data['grid']):
            save_pixel_data(search.id, pixel, is_center=(i==4), position=i)
        
        return jsonify(processed_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)