"""
Asset Search - Search for game assets across multiple platforms
Phase 4: itch.io, Sketchfab, Unity Asset Store (via DuckDuckGo)
"""

import requests
from typing import List, Dict, Optional
import json
from urllib.parse import quote

class AssetSearcher:
    """Main asset search aggregator"""
    
    def __init__(self):
        self.itchio = ItchIOSearcher()
        self.sketchfab = SketchfabSearcher()
        self.unity_store = UnityStoreSearcher()
    
    def search_all(self, query: str, filters: Dict = None) -> Dict:
        """Search across all platforms"""
        filters = filters or {}
        
        results = {
            'query': query,
            'total_results': 0,
            'sources': {}
        }
        
        # Search itch.io
        try:
            itchio_results = self.itchio.search(query, filters)
            results['sources']['itchio'] = itchio_results
            results['total_results'] += len(itchio_results)
        except Exception as e:
            results['sources']['itchio'] = {'error': str(e)}
        
        # Search Sketchfab
        try:
            sketchfab_results = self.sketchfab.search(query, filters)
            results['sources']['sketchfab'] = sketchfab_results
            results['total_results'] += len(sketchfab_results)
        except Exception as e:
            results['sources']['sketchfab'] = {'error': str(e)}
        
        # Search Unity Asset Store
        try:
            unity_results = self.unity_store.search(query, filters)
            results['sources']['unity_asset_store'] = unity_results
            results['total_results'] += len(unity_results)
        except Exception as e:
            results['sources']['unity_asset_store'] = {'error': str(e)}
        
        return results
    
    def filter_results(self, results: Dict, price_type: str = 'all', 
                      asset_type: str = 'all') -> List[Dict]:
        """Filter and combine results"""
        filtered = []
        
        for source, data in results.get('sources', {}).items():
            if isinstance(data, dict) and 'error' not in data:
                for item in data:
                    # Apply filters
                    if price_type == 'free' and not item.get('is_free', False):
                        continue
                    if asset_type != 'all' and item.get('type') != asset_type:
                        continue
                    
                    filtered.append(item)
        
        return filtered


class ItchIOSearcher:
    """itch.io API integration"""
    
    API_BASE = "https://itch.io/api/1"
    
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search itch.io for game assets"""
        
        # Note: itch.io API requires API key for full access
        # This is a simplified search using public endpoints
        
        search_url = f"https://itch.io/search?q={quote(query)}&format=json"
        
        try:
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                # Parse results (simplified)
                results = []
                
                # In production, parse HTML or use official API
                # For now, return mock structure
                results.append({
                    'name': f"Search: {query}",
                    'url': f"https://itch.io/search?q={quote(query)}",
                    'source': 'itch.io',
                    'type': 'assets',
                    'is_free': True,
                    'description': 'Browse results on itch.io'
                })
                
                return results
            
            return []
        
        except requests.RequestException as e:
            return [{'error': str(e)}]


class SketchfabSearcher:
    """Sketchfab API integration"""
    
    API_BASE = "https://api.sketchfab.com/v3"
    
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search Sketchfab for 3D models"""
        
        search_url = f"{self.API_BASE}/search"
        params = {
            'type': 'models',
            'q': query,
            'downloadable': True  # Only downloadable models
        }
        
        if filters:
            if filters.get('free_only'):
                params['downloadable'] = True
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('results', [])[:10]:  # Top 10 results
                    results.append({
                        'name': item.get('name'),
                        'url': item.get('viewerUrl'),
                        'thumbnail': item.get('thumbnails', {}).get('images', [{}])[0].get('url'),
                        'source': 'sketchfab',
                        'type': '3d_model',
                        'is_free': item.get('isDownloadable', False),
                        'author': item.get('user', {}).get('displayName'),
                        'poly_count': item.get('faceCount', 'Unknown')
                    })
                
                return results
            
            return []
        
        except requests.RequestException as e:
            return [{'error': str(e)}]


class UnityStoreSearcher:
    """Unity Asset Store search (via DuckDuckGo - no official API)"""
    
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search Unity Asset Store using DuckDuckGo"""
        
        # Use DuckDuckGo Instant Answer API
        search_query = f"site:assetstore.unity.com {query}"
        ddg_url = f"https://api.duckduckgo.com/"
        
        params = {
            'q': search_query,
            'format': 'json',
            'no_html': 1
        }
        
        try:
            response = requests.get(ddg_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                # Parse related topics
                for topic in data.get('RelatedTopics', [])[:5]:
                    if isinstance(topic, dict) and 'Text' in topic:
                        results.append({
                            'name': topic.get('Text', '').split(' - ')[0],
                            'url': topic.get('FirstURL', ''),
                            'source': 'unity_asset_store',
                            'type': 'asset_pack',
                            'is_free': 'free' in topic.get('Text', '').lower(),
                            'description': topic.get('Text', '')
                        })
                
                # Add direct search link
                results.append({
                    'name': f"Search Unity Asset Store: {query}",
                    'url': f"https://assetstore.unity.com/search?q={quote(query)}",
                    'source': 'unity_asset_store',
                    'type': 'search_link',
                    'is_free': None,
                    'description': 'Browse all results on Unity Asset Store'
                })
                
                return results
            
            return []
        
        except requests.RequestException as e:
            return [{'error': str(e)}]


class AssetRecommender:
    """Recommend assets based on system specs"""
    
    def __init__(self, specs_file='data/system_specs.json'):
        self.specs = self.load_specs(specs_file)
    
    def load_specs(self, file_path):
        """Load system specifications"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def filter_by_performance(self, assets: List[Dict]) -> List[Dict]:
        """Filter assets based on system performance tier"""
        
        if not self.specs:
            return assets
        
        tier = self.specs.get('performance_tier', {}).get('tier', 'medium')
        
        filtered = []
        for asset in assets:
            # Simple filtering logic
            if tier == 'low':
                # Prefer 2D assets and low-poly models
                if '2d' in asset.get('name', '').lower() or \
                   'low poly' in asset.get('name', '').lower():
                    filtered.append(asset)
            elif tier == 'medium':
                # Accept most assets except very high-poly
                if 'high poly' not in asset.get('name', '').lower():
                    filtered.append(asset)
            else:
                # High tier - accept all
                filtered.append(asset)
        
        return filtered if filtered else assets  # Return all if filter too strict
    
    def recommend(self, query: str, filters: Dict = None) -> Dict:
        """Search and recommend based on specs"""
        searcher = AssetSearcher()
        results = searcher.search_all(query, filters)
        
        # Filter by performance
        all_assets = []
        for source, assets in results.get('sources', {}).items():
            if isinstance(assets, list):
                all_assets.extend(assets)
        
        recommended = self.filter_by_performance(all_assets)
        
        return {
            'query': query,
            'system_tier': self.specs.get('performance_tier', {}).get('tier') if self.specs else 'unknown',
            'total_found': len(all_assets),
            'recommended_count': len(recommended),
            'assets': recommended
        }


# Helper function
def search_assets(query: str, free_only: bool = False, asset_type: str = 'all') -> Dict:
    """Quick search function"""
    filters = {
        'free_only': free_only,
        'asset_type': asset_type
    }
    
    searcher = AssetSearcher()
    return searcher.search_all(query, filters)


def recommend_assets(query: str) -> Dict:
    """Quick recommendation function"""
    recommender = AssetRecommender()
    return recommender.recommend(query)