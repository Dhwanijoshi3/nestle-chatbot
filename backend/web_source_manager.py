# backend/web_source_manager.py - Web Source Management

from typing import List, Dict, Any

class WebSourceManager:
    """Manages web sources and scraping for additional context"""
    
    def __init__(self):
        self.base_urls = {
            'main': 'https://www.madewithnestle.ca',
            'corporate': 'https://corporate.nestle.ca',
            'sustainability': 'https://www.madewithnestle.ca/sustainability',
            'recipes': 'https://www.madewithnestle.ca/recipes',
            'brands': 'https://www.madewithnestle.ca/brands'
        }
        
        self.product_urls = {
            'kitkat': 'https://www.madewithnestle.ca/brands/kitkat',
            'smarties': 'https://www.madewithnestle.ca/brands/smarties',
            'aero': 'https://www.madewithnestle.ca/brands/aero',
            'coffee-mate': 'https://www.madewithnestle.ca/brands/coffee-mate',
            'quality street': 'https://www.madewithnestle.ca/brands/quality-street'
        }
    
    async def get_relevant_sources(self, user_query: str, entities: List[str]) -> List[str]:
        """Get relevant web sources based on query and entities"""
        
        sources = []
        query_lower = user_query.lower()
        
        # Add entity-specific URLs
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower in self.product_urls:
                sources.append(self.product_urls[entity_lower])
        
        # Add intent-based URLs
        if any(word in query_lower for word in ['sustainability', 'environment', 'green', 'cocoa']):
            sources.append(self.base_urls['sustainability'])
        
        if any(word in query_lower for word in ['recipe', 'cooking', 'baking']):
            sources.append(self.base_urls['recipes'])
        
        if any(word in query_lower for word in ['company', 'corporate', 'ceo', 'leadership']):
            sources.append(self.base_urls['corporate'])
        
        if any(word in query_lower for word in ['brand', 'product']):
            sources.append(self.base_urls['brands'])
        
        # Always include main site if no specific sources
        if not sources:
            sources.append(self.base_urls['main'])
        
        # Remove duplicates and limit
        return list(set(sources))[:4]