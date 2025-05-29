# backend/context_retriever.py - Neo4j Graph Context Retrieval

from typing import Dict, List, Any, Optional
from .neo4j_connection import neo4j_conn

class ContextRetriever:
    """Retrieves relevant context from Neo4j graph based on query analysis"""
    
    def __init__(self):
        pass
    
    async def get_relevant_context(self, query: str, intent: str, entities: List[str]) -> Dict[str, Any]:
        """Get relevant context from Neo4j graph"""
        
        try:
            with neo4j_conn.get_session() as session:
                context = {
                    'nodes': [],
                    'relationships': [],
                    'paths': [],
                    'summary': ''
                }
                
                # Strategy 1: Direct entity lookup
                if entities:
                    entity_context = self._get_entity_context(session, entities)
                    context['nodes'].extend(entity_context['nodes'])
                    context['relationships'].extend(entity_context['relationships'])
                
                # Strategy 2: Intent-based context retrieval
                intent_context = self._get_intent_based_context(session, intent, query)
                context['nodes'].extend(intent_context['nodes'])
                context['relationships'].extend(intent_context['relationships'])
                
                # Strategy 3: Semantic similarity search
                semantic_context = self._get_semantic_context(session, query)
                context['nodes'].extend(semantic_context['nodes'])
                
                # Strategy 4: Get relationship paths between found entities
                if len([n for n in context['nodes'] if n]) >= 2:
                    paths = self._get_relationship_paths(session, context['nodes'])
                    context['paths'] = paths
                
                # Remove duplicates and create summary
                context = self._deduplicate_context(context)
                context['summary'] = self._create_context_summary(context)
                
                return context
                
        except Exception as e:
            print(f"Error retrieving context: {e}")
            return {'nodes': [], 'relationships': [], 'paths': [], 'summary': ''}
    
    def _get_entity_context(self, session, entities: List[str]) -> Dict[str, Any]:
        """Get context for specific entities"""
        
        nodes = []
        relationships = []
        
        for entity in entities:
            # Find the entity node
            entity_query = """
            MATCH (n)
            WHERE toLower(n.name) = toLower($entity_name)
            RETURN n, labels(n) as labels
            LIMIT 1
            """
            
            result = session.run(entity_query, {'entity_name': entity})
            record = result.single()
            
            if record:
                node_data = dict(record['n'])
                node_labels = record['labels']
                
                nodes.append({
                    'name': node_data.get('name', entity),
                    'type': node_labels[0] if node_labels else 'Unknown',
                    'properties': node_data,
                    'relevance': 'direct_match'
                })
                
                # Get relationships for this entity
                rel_query = """
                MATCH (n)-[r]-(m)
                WHERE toLower(n.name) = toLower($entity_name)
                RETURN n, r, m, labels(m) as target_labels
                LIMIT 10
                """
                
                rel_results = session.run(rel_query, {'entity_name': entity})
                
                for rel_record in rel_results:
                    rel_data = dict(rel_record['r'])
                    target_data = dict(rel_record['m'])
                    target_labels = rel_record['target_labels']
                    
                    relationships.append({
                        'from': node_data.get('name', entity),
                        'to': target_data.get('name', 'Unknown'),
                        'type': rel_record['r'].type,
                        'properties': rel_data
                    })
                    
                    # Add target node if not already included
                    target_node = {
                        'name': target_data.get('name', 'Unknown'),
                        'type': target_labels[0] if target_labels else 'Unknown',
                        'properties': target_data,
                        'relevance': 'connected_to_entity'
                    }
                    
                    if target_node not in nodes:
                        nodes.append(target_node)
        
        return {'nodes': nodes, 'relationships': relationships}
    
    def _get_intent_based_context(self, session, intent: str, query: str) -> Dict[str, Any]:
        """Get context based on query intent"""
        
        nodes = []
        relationships = []
        
        if intent == 'company_info':
            # Get company-related information
            company_query = """
            MATCH (n)
            WHERE n.name CONTAINS 'Nestlé' OR n.name CONTAINS 'Nestle' 
               OR 'Company' IN labels(n) OR 'Brand' IN labels(n)
            RETURN n, labels(n) as labels
            LIMIT 5
            """
            
            results = session.run(company_query)
            for record in results:
                node_data = dict(record['n'])
                node_labels = record['labels']
                
                nodes.append({
                    'name': node_data.get('name', 'Unknown'),
                    'type': node_labels[0] if node_labels else 'Unknown',
                    'properties': node_data,
                    'relevance': 'intent_company'
                })
        
        elif intent == 'sustainability':
            # Get sustainability-related information
            sustainability_query = """
            MATCH (n)
            WHERE toLower(n.name) CONTAINS 'sustainability' 
               OR toLower(n.name) CONTAINS 'cocoa'
               OR toLower(n.name) CONTAINS 'environment'
               OR 'Topic' IN labels(n)
            RETURN n, labels(n) as labels
            LIMIT 5
            """
            
            results = session.run(sustainability_query)
            for record in results:
                node_data = dict(record['n'])
                node_labels = record['labels']
                
                nodes.append({
                    'name': node_data.get('name', 'Unknown'),
                    'type': node_labels[0] if node_labels else 'Unknown',
                    'properties': node_data,
                    'relevance': 'intent_sustainability'
                })
        
        elif intent == 'product_info':
            # Get product-related information
            product_query = """
            MATCH (n)
            WHERE 'Product' IN labels(n) OR 'Category' IN labels(n)
            RETURN n, labels(n) as labels
            LIMIT 8
            """
            
            results = session.run(product_query)
            for record in results:
                node_data = dict(record['n'])
                node_labels = record['labels']
                
                nodes.append({
                    'name': node_data.get('name', 'Unknown'),
                    'type': node_labels[0] if node_labels else 'Unknown',
                    'properties': node_data,
                    'relevance': 'intent_product'
                })
        
        return {'nodes': nodes, 'relationships': relationships}
    
    def _get_semantic_context(self, session, query: str) -> Dict[str, Any]:
        """Get context using semantic/keyword matching"""
        
        nodes = []
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        for keyword in keywords[:3]:  # Limit to top 3 keywords
            keyword_query = """
            MATCH (n)
            WHERE toLower(n.name) CONTAINS toLower($keyword)
               OR toLower(n.description) CONTAINS toLower($keyword)
            RETURN n, labels(n) as labels
            LIMIT 3
            """
            
            results = session.run(keyword_query, {'keyword': keyword})
            for record in results:
                node_data = dict(record['n'])
                node_labels = record['labels']
                
                nodes.append({
                    'name': node_data.get('name', 'Unknown'),
                    'type': node_labels[0] if node_labels else 'Unknown',
                    'properties': node_data,
                    'relevance': f'keyword_{keyword}'
                })
        
        return {'nodes': nodes}
    
    def _get_relationship_paths(self, session, nodes: List[Dict]) -> List[Dict]:
        """Find relationship paths between entities"""
        
        paths = []
        
        if len(nodes) < 2:
            return paths
        
        try:
            # Find paths between first two relevant nodes
            node1_name = nodes[0].get('name')
            node2_name = nodes[1].get('name') if len(nodes) > 1 else None
            
            if node1_name and node2_name:
                path_query = """
                MATCH path = (a)-[*1..3]-(b)
                WHERE toLower(a.name) = toLower($node1) 
                  AND toLower(b.name) = toLower($node2)
                RETURN path
                LIMIT 3
                """
                
                results = session.run(path_query, {
                    'node1': node1_name, 
                    'node2': node2_name
                })
                
                for record in results:
                    path_data = record['path']
                    paths.append({
                        'start': node1_name,
                        'end': node2_name,
                        'length': len(path_data.relationships),
                        'relationships': [rel.type for rel in path_data.relationships]
                    })
        
        except Exception as e:
            print(f"Error finding paths: {e}")
        
        return paths
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are',
            'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can',
            'what', 'when', 'where', 'why', 'how', 'tell', 'me', 'please', 'who'
        }
        
        import re
        words = re.findall(r'\b\w{3,}\b', query.lower())
        keywords = [word for word in words if word not in stop_words]
        
        return keywords[:5]  # Return top 5 keywords
    
    def _deduplicate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Remove duplicate nodes and relationships"""
        
        # Deduplicate nodes by name
        seen_nodes = set()
        unique_nodes = []
        
        for node in context['nodes']:
            node_key = (node.get('name', ''), node.get('type', ''))
            if node_key not in seen_nodes:
                seen_nodes.add(node_key)
                unique_nodes.append(node)
        
        # Deduplicate relationships
        seen_rels = set()
        unique_rels = []
        
        for rel in context['relationships']:
            rel_key = (rel.get('from', ''), rel.get('to', ''), rel.get('type', ''))
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                unique_rels.append(rel)
        
        return {
            'nodes': unique_nodes,
            'relationships': unique_rels,
            'paths': context['paths'],
            'summary': context['summary']
        }
    
    def _create_context_summary(self, context: Dict[str, Any]) -> str:
        """Create a summary of retrieved context"""
        
        nodes = context['nodes']
        relationships = context['relationships']
        
        if not nodes:
            return "No relevant information found in knowledge graph."
        
        summary_parts = []
        
        # Summarize nodes by type
        node_types = {}
        for node in nodes:
            node_type = node.get('type', 'Unknown')
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node.get('name', 'Unknown'))
        
        for node_type, names in node_types.items():
            if len(names) == 1:
                summary_parts.append(f"{node_type}: {names[0]}")
            else:
                summary_parts.append(f"{node_type}s: {', '.join(names[:3])}")
        
        # Add relationship info
        if relationships:
            rel_types = list(set([rel.get('type', 'Unknown') for rel in relationships]))
            summary_parts.append(f"Related through: {', '.join(rel_types[:3])}")
        
        return "; ".join(summary_parts)