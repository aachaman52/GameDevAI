"""
Asset Search - Multi-platform asset search
Phase 4 implementation
"""

import requests
from typing import List, Dict
from urllib.parse import quote

class AssetSearcher:
    def __init__(self):
        self.itchio = ItchIOSearcher()
        self.unity_store = UnityStoreSearcher()
    
    def search_all(self, query: str, filters: Dict = None) -> Dict:
        filters = filters or {}
        
        results = {
            'query': query,
            'total_results': 0,
            'sources': {}
        }
        
        try:
            itchio_results = self.itchio.search(query, filters)
            results['sources']['itchio'] = itchio_results
            results['total_results'] += len(itchio_results)
        except Exception as e:
            results['sources']['itchio'] = {'error': str(e)}
        
        try:
            unity_results = self.unity_store.search(query, filters)
            results['sources']['unity_asset_store'] = unity_results
            results['total_results'] += len(unity_results)
        except Exception as e:
            results['sources']['unity_asset_store'] = {'error': str(e)}
        
        return results

class ItchIOSearcher:
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        search_url = f"https://itch.io/search?q={quote(query)}"
        
        results = [{
            'name': f"Search results for: {query}",
            'url': search_url,
            'source': 'itch.io',
            'type': 'assets',
            'is_free': True,
            'description': 'Browse results on itch.io'
        }]
        
        return results

class UnityStoreSearcher:
    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        search_url = f"https://assetstore.unity.com/search?q={quote(query)}"
        
        results = [{
            'name': f"Unity Asset Store: {query}",
            'url': search_url,
            'source': 'unity_asset_store',
            'type': 'search_link',
            'is_free': None,
            'description': 'Browse all results on Unity Asset Store'
        }]
        
        return results

def search_assets(query: str, free_only: bool = False) -> Dict:
    filters = {'free_only': free_only}
    searcher = AssetSearcher()
    return searcher.search_all(query, filters)