# from .neo4j_connection import neo4j_conn

# class GraphSchema:
#     def __init__(self):
#         self.constraints_and_indexes = [
#             # Unique constraints
#             "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
#             "CREATE CONSTRAINT document_url IF NOT EXISTS FOR (d:Document) REQUIRE d.url IS UNIQUE",
#             "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
#             "CREATE CONSTRAINT brand_name IF NOT EXISTS FOR (b:Brand) REQUIRE b.name IS UNIQUE",
            
#             # Indexes for performance
#             "CREATE INDEX product_description IF NOT EXISTS FOR (p:Product) ON (p.description)",
#             "CREATE INDEX document_content IF NOT EXISTS FOR (d:Document) ON (d.content)",
#             "CREATE INDEX topic_name IF NOT EXISTS FOR (t:Topic) ON (t.name)",
#             "CREATE INDEX keyword_text IF NOT EXISTS FOR (k:Keyword) ON (k.text)",
#         ]
    
#     def setup_schema(self):
#         """Create constraints and indexes"""
#         print("🏗️ Setting up Neo4j schema...")
        
#         with neo4j_conn.get_session() as session:
#             for constraint in self.constraints_and_indexes:
#                 try:
#                     session.run(constraint)
#                     print(f"✅ Applied: {constraint[:50]}...")
#                 except Exception as e:
#                     if "already exists" in str(e).lower():
#                         print(f"⚠️ Already exists: {constraint[:50]}...")
#                     else:
#                         print(f"❌ Failed: {constraint[:50]}... Error: {e}")
        
#         print("✅ Schema setup complete")
    
#     def clear_database(self):
#         """Clear all data (use with caution!)"""
#         with neo4j_conn.get_session() as session:
#             session.run("MATCH (n) DETACH DELETE n")
#         print("🗑️ Database cleared")

# schema_manager = GraphSchema()
from .neo4j_connection import neo4j_conn

class GraphSchema:
    def __init__(self):
        self.constraints_and_indexes = [
            "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT category_name IF NOT EXISTS FOR (c:Category) REQUIRE c.name IS UNIQUE",
            "CREATE INDEX product_description IF NOT EXISTS FOR (p:Product) ON (p.description)",
            "CREATE INDEX topic_name IF NOT EXISTS FOR (t:Topic) ON (t.name)",
        ]
    
    def setup_schema(self):
        print("🏗️ Setting up Neo4j schema...")
        
        try:
            with neo4j_conn.get_session() as session:
                for constraint in self.constraints_and_indexes:
                    try:
                        session.run(constraint)
                        print(f"✅ Applied: {constraint[:50]}...")
                    except Exception as e:
                        if "already exists" in str(e).lower():
                            print(f"⚠️ Already exists: {constraint[:50]}...")
                        else:
                            print(f"❌ Failed: {constraint[:50]}... Error: {e}")
            
            print("✅ Schema setup complete")
        except Exception as e:
            print(f"❌ Schema setup failed: {e}")

schema_manager = GraphSchema()
