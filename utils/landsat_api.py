from landsatxplore.api import API
from landsatxplore.earthexplorer import EarthExplorer
import rasterio
import numpy as np
from datetime import datetime, timedelta

class LandsatAPI:
    def __init__(self, username, password):
        self.api = API(username, password)
        self.ee = EarthExplorer(username, password)
    
    def search_scenes(self, lat, lon, start_date=None, end_date=None):
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        scenes = self.api.search(
            dataset='landsat_ot_c2_l2',
            latitude=lat,
            longitude=lon,
            start_date=start_date,
            end_date=end_date,
            max_cloud_cover=50
        )
        
        return [{'scene_id': scene['entity_id'],
                'cloud_cover': scene['cloud_cover'],
                'date': scene['acquisition_date']} for scene in scenes]
    
    def get_pixel_data(self, scene_id, lat, lon):
        # Download scene (this is simplified - you'd need error handling and cleanup)
        self.ee.download(scene_id, output_dir='temp')
        
        # Process downloaded scene to get 3x3 grid centered on lat/lon
        # This is a simplified version - actual implementation would need more robustness
        with rasterio.open(f'temp/{scene_id}_SR_B2.TIF') as src:
            row, col = src.index(lon, lat)
            window = rasterio.windows.Window(col-1, row-1, 3, 3)
            grid_data = {}
            
            for band in range(2, 8):  # Landsat 8/9 bands
                with rasterio.open(f'temp/{scene_id}_SR_B{band}.TIF') as src:
                    grid_data[f'B{band}'] = src.read(1, window=window)
        
        return grid_data
    
    def __del__(self):
        self.api.logout()
        self.ee.logout()