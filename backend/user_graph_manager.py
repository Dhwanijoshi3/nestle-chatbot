# from .neo4j_connection import neo4j_conn

# class UserGraphManager:
#     """Allows users to customize the knowledge graph"""
    
#     def add_custom_node(self, node_type, name, properties=None):
#         """Add a custom node to the graph"""
#         if properties is None:
#             properties = {}
        
#         with neo4j_conn.get_session() as session:
#             # Create the node with custom label
#             query = f"""
#             CREATE (n:{node_type} {{name: $name}})
#             SET n += $properties
#             SET n.custom_added = true
#             SET n.created_at = datetime()
#             RETURN n
#             """
            
#             try:
#                 result = session.run(query, {
#                     'name': name, 
#                     'properties': properties
#                 })
#                 return {"success": True, "message": f"Added {node_type} node: {name}"}
#             except Exception as e:
#                 return {"success": False, "message": f"Error: {str(e)}"}
    
#     def add_custom_relationship(self, from_node, to_node, relationship_type, properties=None):
#         """Add a custom relationship between nodes"""
#         if properties is None:
#             properties = {}
        
#         with neo4j_conn.get_session() as session:
#             query = f"""
#             MATCH (a), (b)
#             WHERE a.name = $from_node AND b.name = $to_node
#             CREATE (a)-[r:{relationship_type}]->(b)
#             SET r += $properties
#             SET r.custom_added = true
#             SET r.created_at = datetime()
#             RETURN r
#             """
            
#             try:
#                 result = session.run(query, {
#                     'from_node': from_node,
#                     'to_node': to_node,
#                     'properties': properties
#                 })
#                 return {"success": True, "message": f"Added relationship: {from_node} -{relationship_type}-> {to_node}"}
#             except Exception as e:
#                 return {"success": False, "message": f"Error: {str(e)}"}
    
#     def get_graph_stats(self):
#         """Get statistics about the current graph"""
#         with neo4j_conn.get_session() as session:
#             stats_query = """
#             MATCH (n)
#             RETURN labels(n) as label, count(n) as count
#             ORDER BY count DESC
#             """
            
#             results = session.run(stats_query)
#             stats = {}
            
#             for record in results:
#                 label = record['label'][0] if record['label'] else 'Unknown'
#                 stats[label] = record['count']
            
#             # Get relationship counts
#             rel_query = """
#             MATCH ()-[r]->()
#             RETURN type(r) as relationship_type, count(r) as count
#             ORDER BY count DESC
#             """
            
#             rel_results = session.run(rel_query)
#             relationships = {}
            
#             for record in rel_results:
#                 relationships[record['relationship_type']] = record['count']
            
#             return {
#                 'nodes': stats,
#                 'relationships': relationships,
#                 'total_nodes': sum(stats.values()),
#                 'total_relationships': sum(relationships.values())
#             }
    
#     def search_nodes(self, search_term, node_type=None):
#         """Search for nodes in the graph"""
#         with neo4j_conn.get_session() as session:
#             if node_type:
#                 query = f"""
#                 MATCH (n:{node_type})
#                 WHERE toLower(n.name) CONTAINS toLower($search_term)
#                 RETURN n.name as name, labels(n) as labels
#                 LIMIT 20
#                 """
#             else:
#                 query = """
#                 MATCH (n)
#                 WHERE toLower(n.name) CONTAINS toLower($search_term)
#                 RETURN n.name as name, labels(n) as labels
#                 LIMIT 20
#                 """
            
#             results = session.run(query, {'search_term': search_term})
#             return [{'name': record['name'], 'type': record['labels'][0]} for record in results]

# user_graph_manager = UserGraphManager()

from .neo4j_connection import neo4j_conn

class UserGraphManager:
    """Manage user interactions with the knowledge graph"""
    
    def add_custom_node(self, node_type, name, properties=None):
        if properties is None:
            properties = {}
        
        try:
            with neo4j_conn.get_session() as session:
                query = f"""
                CREATE (n:{node_type} {{name: $name}})
                SET n += $properties
                SET n.custom_added = true
                SET n.created_at = datetime()
                RETURN n
                """
                
                session.run(query, {
                    'name': name, 
                    'properties': properties
                })
                return {"success": True, "message": f"Added {node_type} node: {name}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def add_custom_relationship(self, from_node, to_node, relationship_type, properties=None):
        if properties is None:
            properties = {}
        
        try:
            with neo4j_conn.get_session() as session:
                query = f"""
                MATCH (a), (b)
                WHERE a.name = $from_node AND b.name = $to_node
                CREATE (a)-[r:{relationship_type}]->(b)
                SET r += $properties
                SET r.custom_added = true
                SET r.created_at = datetime()
                RETURN r
                """
                
                session.run(query, {
                    'from_node': from_node,
                    'to_node': to_node,
                    'properties': properties
                })
                return {"success": True, "message": f"Added relationship: {from_node} -{relationship_type}-> {to_node}"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def get_graph_stats(self):
        try:
            with neo4j_conn.get_session() as session:
                node_query = """
                MATCH (n)
                UNWIND labels(n) as label
                WITH label, count(*) as count
                RETURN label, count
                ORDER BY count DESC
                """
                
                node_results = session.run(node_query)
                nodes = {}
                for record in node_results:
                    nodes[record['label']] = record['count']
                
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
                """
                
                rel_results = session.run(rel_query)
                relationships = {}
                for record in rel_results:
                    relationships[record['relationship_type']] = record['count']
                
                return {
                    'nodes': nodes,
                    'relationships': relationships,
                    'total_nodes': sum(nodes.values()),
                    'total_relationships': sum(relationships.values())
                }
        except Exception as e:
            return {
                'error': f"Failed to get stats: {str(e)}",
                'nodes': {},
                'relationships': {},
                'total_nodes': 0,
                'total_relationships': 0
            }
    
    def search_nodes(self, search_term, node_type=None):
        try:
            with neo4j_conn.get_session() as session:
                if node_type:
                    query = f"""
                    MATCH (n:{node_type})
                    WHERE toLower(n.name) CONTAINS toLower($search_term)
                    RETURN n.name as name, labels(n) as labels
                    LIMIT 20
                    """
                else:
                    query = """
                    MATCH (n)
                    WHERE toLower(n.name) CONTAINS toLower($search_term)
                    RETURN n.name as name, labels(n) as labels
                    LIMIT 20
                    """
                
                results = session.run(query, {'search_term': search_term})
                return [{'name': record['name'], 'type': record['labels'][0]} for record in results]
        except Exception as e:
            return []

user_graph_manager = UserGraphManager()
