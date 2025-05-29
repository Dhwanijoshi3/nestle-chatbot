# from neo4j import GraphDatabase
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Neo4jConnection:
#     def __init__(self):
#         self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
#         self.user = os.getenv("NEO4J_USER", "neo4j")
#         self.password = os.getenv("NEO4J_PASSWORD")
#         self.database = os.getenv("NEO4J_DATABASE", "neo4j")
#         self.driver = None
        
#     def connect(self):
#         """Establish connection to Neo4j database"""
#         try:
#             self.driver = GraphDatabase.driver(
#                 self.uri, 
#                 auth=(self.user, self.password)
#             )
#             # Test connection
#             with self.driver.session(database=self.database) as session:
#                 result = session.run("RETURN 'Connection successful' as message")
#                 print(f"✅ Neo4j connected: {result.single()['message']}")
#             return True
#         except Exception as e:
#             print(f"❌ Neo4j connection failed: {e}")
#             return False
    
#     def close(self):
#         """Close the connection"""
#         if self.driver:
#             self.driver.close()
#             print("🔌 Neo4j connection closed")
    
#     def get_session(self):
#         """Get a database session"""
#         if not self.driver:
#             if not self.connect():
#                 raise Exception("Failed to connect to Neo4j")
#         return self.driver.session(database=self.database)

# # Global connection instance
# neo4j_conn = Neo4jConnection()
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jConnection:
    def __init__(self):
        #self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 'Connection successful' as message")
                print(f"✅ Neo4j connected: {result.single()['message']}")
            return True
        except Exception as e:
            print(f"❌ Neo4j connection failed: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.driver:
            self.driver.close()
            print("🔌 Neo4j connection closed")
    
    def get_session(self):
        """Get a database session"""
        if not self.driver:
            if not self.connect():
                raise Exception("Failed to connect to Neo4j")
        return self.driver.session(database=self.database)

# Global connection instance
neo4j_conn = Neo4jConnection()
