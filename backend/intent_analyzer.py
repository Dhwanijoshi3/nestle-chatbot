# backend/intent_analyzer.py - Enhanced Query Intent Analysis

import re
from typing import Dict, List, Any
from .neo4j_connection import neo4j_conn

class IntentAnalyzer:
    """Analyzes user queries to determine intent and extract entities"""
    
    def __init__(self):
        self.intent_patterns = {
            'product_info': {
                'patterns': [
                    r'\b(what is|tell me about|information about|describe|explain)\b.*\b(kitkat|smarties|aero|coffee.?mate|quality street|nespresso|milo)\b',
                    r'\b(kitkat|smarties|aero|coffee.?mate|quality street|nespresso|milo)\b.*\b(product|brand|information|details)\b'
                ],
                'keywords': ['product', 'brand', 'what is', 'tell me about', 'information', 'describe']
            },
            'company_info': {
                'patterns': [
                    r'\b(who is|who are|tell me about|information about)\b.*\b(ceo|president|leader|management|executive|chief|runs|boss)\b',
                    r'\b(ceo|president|leader|management|executive|chief|runs|boss)\b.*\b(nestlé|nestle|company)\b',
                    r'\b(nestlé|nestle)\b.*\b(company|business|corporation|history|founded|headquarters|leadership|management)\b',
                    r'\b(who runs|who leads|who manages|who is in charge|who is the ceo)\b'
                ],
                'keywords': ['ceo', 'president', 'leader', 'company', 'nestlé', 'nestle', 'management', 'executive', 'founded', 'headquarters', 'runs', 'leads', 'boss', 'chief']
            },
            'sustainability': {
                'patterns': [
                    r'\b(sustainability|sustainable|environment|eco|green|carbon|cocoa plan|water)\b',
                    r'\b(climate|footprint|emissions|renewable|recycling|responsible)\b'
                ],
                'keywords': ['sustainability', 'sustainable', 'environment', 'eco', 'green', 'carbon', 'cocoa plan']
            },
            'availability': {
                'patterns': [
                    r'\b(where|how|can i)\b.*(buy|find|purchase|get|order)\b',
                    r'\b(store|shop|retail|location|available)\b'
                ],
                'keywords': ['where to buy', 'find', 'purchase', 'store', 'available', 'location']
            },
            'comparison': {
                'patterns': [
                    r'\b(compare|comparison|difference|versus|vs|better|best|prefer)\b',
                    r'\b(which is|what\'s the difference|how do they differ)\b'
                ],
                'keywords': ['compare', 'difference', 'versus', 'vs', 'better', 'which']
            },
            'nutrition': {
                'patterns': [
                    r'\b(nutrition|nutritional|health|healthy|calories|ingredients|diet)\b',
                    r'\b(vitamin|mineral|protein|fat|sugar|sodium)\b'
                ],
                'keywords': ['nutrition', 'health', 'calories', 'ingredients', 'healthy']
            },
            'recipes': {
                'patterns': [
                    r'\b(recipe|cooking|baking|cook|bake|make|preparation)\b',
                    r'\b(how to make|how do i make|cooking with|baking with)\b'
                ],
                'keywords': ['recipe', 'cooking', 'baking', 'how to make']
            }
        }
        
        # Known Nestlé entities
        self.entity_patterns = {
            'products': [
                ('kitkat', 'KitKat'),
                ('kit kat', 'KitKat'),
                ('smarties', 'Smarties'),
                ('aero', 'Aero'),
                ('coffee.?mate', 'Coffee-mate'),
                ('quality street', 'Quality Street'),
                ('nespresso', 'Nespresso'),
                ('carnation', 'Carnation'),
                ('gerber', 'Gerber'),
                ('butterfinger', 'Butterfinger'),
                ('milo', 'MILO'),
                ('nido', 'NIDO'),
                ('garden gourmet', 'Garden Gourmet')
            ],
            'people': [
                ('mark schneider', 'Mark Schneider'),
                ('paul bulcke', 'Paul Bulcke'),
                ('henri nestlé', 'Henri Nestlé'),
                ('henri nestle', 'Henri Nestlé')
            ],
            'locations': [
                ('canada', 'Canada'),
                ('toronto', 'Toronto'),
                ('switzerland', 'Switzerland'),
                ('vevey', 'Vevey')
            ],
            'concepts': [
                ('cocoa plan', 'Cocoa Plan'),
                ('nestlé cocoa plan', 'Nestlé Cocoa Plan'),
                ('good food good life', 'Good Food Good Life'),
                ('sustainability', 'Sustainability')
            ]
        }
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine intent and extract entities"""
        
        query_lower = query.lower().strip()
        
        # Determine intent
        intent = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query_lower)
        
        # Get additional context from Neo4j if entities found
        graph_entities = await self._get_graph_entities(entities)
        
        return {
            'intent': intent,
            'entities': entities,
            'graph_entities': graph_entities,
            'query_type': self._determine_query_type(query),
            'confidence': self._calculate_confidence(query_lower, intent, entities)
        }
    
    def _classify_intent(self, query_lower: str) -> str:
        """Classify the intent of the query"""
        
        intent_scores = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            
            # Check pattern matches
            for pattern in config['patterns']:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 3
            
            # Check keyword matches
            for keyword in config['keywords']:
                if keyword.lower() in query_lower:
                    score += 1
            
            intent_scores[intent] = score
        
        # Return highest scoring intent, or 'general_info' if no clear match
        if intent_scores and max(intent_scores.values()) > 0:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general_info'
    
    def _extract_entities(self, query_lower: str) -> List[str]:
        """Extract entities from the query"""
        
        found_entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern, entity_name in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    found_entities.append(entity_name)
        
        return list(set(found_entities))  # Remove duplicates
    
    async def _get_graph_entities(self, entities: List[str]) -> List[Dict[str, Any]]:
        """Get additional information about entities from Neo4j"""
        
        if not entities:
            return []
        
        graph_entities = []
        
        try:
            with neo4j_conn.get_session() as session:
                for entity in entities:
                    # Search for entity in graph
                    query = """
                    MATCH (n)
                    WHERE toLower(n.name) = toLower($entity_name)
                    RETURN n, labels(n) as labels
                    LIMIT 1
                    """
                    
                    result = session.run(query, {'entity_name': entity})
                    record = result.single()
                    
                    if record:
                        node_data = dict(record['n'])
                        node_labels = record['labels']
                        
                        graph_entities.append({
                            'name': entity,
                            'type': node_labels[0] if node_labels else 'Unknown',
                            'properties': node_data,
                            'found_in_graph': True
                        })
                    else:
                        graph_entities.append({
                            'name': entity,
                            'type': 'Unknown',
                            'found_in_graph': False
                        })
        
        except Exception as e:
            print(f"Error getting graph entities: {e}")
        
        return graph_entities
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query (question, request, etc.)"""
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['?', 'what', 'how', 'why', 'when', 'where', 'who']):
            return 'question'
        elif any(word in query_lower for word in ['tell me', 'explain', 'describe', 'show me']):
            return 'request_info'
        elif any(word in query_lower for word in ['find', 'search', 'look for']):
            return 'search'
        elif any(word in query_lower for word in ['compare', 'difference']):
            return 'comparison'
        else:
            return 'statement'
    
    def _calculate_confidence(self, query_lower: str, intent: str, entities: List[str]) -> float:
        """Calculate confidence score for the analysis"""
        
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on clear intent patterns
        if intent in self.intent_patterns:
            for pattern in self.intent_patterns[intent]['patterns']:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    confidence += 0.2
        
        # Increase confidence based on entity recognition
        confidence += min(len(entities) * 0.1, 0.3)
        
        # Increase confidence for clear question structure
        if any(word in query_lower for word in ['what', 'how', 'why', 'who', 'where']):
            confidence += 0.1
        
        return min(confidence, 1.0)