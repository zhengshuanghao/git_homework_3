"""
高德地图服务
"""
import requests
from config import Config


class AmapService:
    """高德地图服务类"""
    
    def __init__(self):
        self.api_key = Config.AMAP_API_KEY
        self.api_secret = Config.AMAP_API_SECRET
        self.base_url = "https://restapi.amap.com/v3"
    
    def is_configured(self):
        """检查配置是否完整"""
        return bool(self.api_key)
    
    def geocode(self, address):
        """地理编码 - 将地址转换为经纬度"""
        if not self.is_configured():
            return None
        
        url = f"{self.base_url}/geocode/geo"
        params = {
            'key': self.api_key,
            'address': address
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1' and data.get('geocodes'):
                location = data['geocodes'][0]['location'].split(',')
                return {
                    'lng': float(location[0]),
                    'lat': float(location[1]),
                    'formatted_address': data['geocodes'][0].get('formatted_address', '')
                }
            return None
        except Exception as e:
            print(f"地理编码失败: {str(e)}")
            return None
    
    def reverse_geocode(self, lng, lat):
        """逆地理编码 - 将经纬度转换为地址"""
        if not self.is_configured():
            return None
        
        url = f"{self.base_url}/geocode/regeo"
        params = {
            'key': self.api_key,
            'location': f"{lng},{lat}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1' and data.get('regeocode'):
                return {
                    'address': data['regeocode'].get('formatted_address', ''),
                    'province': data['regeocode'].get('addressComponent', {}).get('province', ''),
                    'city': data['regeocode'].get('addressComponent', {}).get('city', ''),
                    'district': data['regeocode'].get('addressComponent', {}).get('district', '')
                }
            return None
        except Exception as e:
            print(f"逆地理编码失败: {str(e)}")
            return None
    
    def search_poi(self, keywords, city='', types=''):
        """搜索POI（兴趣点）"""
        if not self.is_configured():
            return []
        
        url = f"{self.base_url}/place/text"
        params = {
            'key': self.api_key,
            'keywords': keywords,
            'city': city,
            'types': types,
            'offset': 20,
            'page': 1,
            'extensions': 'all'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1' and data.get('pois'):
                pois = []
                for poi in data['pois']:
                    location = poi.get('location', '').split(',')
                    if len(location) == 2:
                        pois.append({
                            'id': poi.get('id', ''),
                            'name': poi.get('name', ''),
                            'type': poi.get('type', ''),
                            'address': poi.get('address', ''),
                            'lng': float(location[0]),
                            'lat': float(location[1]),
                            'tel': poi.get('tel', ''),
                            'distance': poi.get('distance', 0)
                        })
                return pois
            return []
        except Exception as e:
            print(f"搜索POI失败: {str(e)}")
            return []
    
    def get_direction(self, origin, destination, strategy=0):
        """路径规划
        strategy: 0-速度优先, 1-费用优先, 2-距离优先, 3-不走高速
        """
        if not self.is_configured():
            return None
        
        url = f"{self.base_url}/direction/driving"
        params = {
            'key': self.api_key,
            'origin': f"{origin['lng']},{origin['lat']}",
            'destination': f"{destination['lng']},{destination['lat']}",
            'strategy': strategy,
            'extensions': 'all'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1' and data.get('route'):
                route = data['route']
                paths = route.get('paths', [])
                if paths:
                    path = paths[0]
                    steps = path.get('steps', [])
                    polyline = []
                    for step in steps:
                        # 解码polyline
                        polyline.extend(self._decode_polyline(step.get('polyline', '')))
                    
                    return {
                        'distance': path.get('distance', 0),
                        'duration': path.get('duration', 0),
                        'tolls': path.get('tolls', 0),
                        'polyline': polyline
                    }
            return None
        except Exception as e:
            print(f"路径规划失败: {str(e)}")
            return None
    
    def _decode_polyline(self, polyline_str):
        """解码polyline字符串为坐标列表"""
        coordinates = []
        index = 0
        lat = 0
        lng = 0
        
        while index < len(polyline_str):
            # 解码纬度
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlat = ~(result >> 1) if (result & 1) != 0 else (result >> 1)
            lat += dlat
            
            # 解码经度
            shift = 0
            result = 0
            while True:
                b = ord(polyline_str[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dlng = ~(result >> 1) if (result & 1) != 0 else (result >> 1)
            lng += dlng
            
            coordinates.append({
                'lat': lat * 1e-5,
                'lng': lng * 1e-5
            })
        
        return coordinates










