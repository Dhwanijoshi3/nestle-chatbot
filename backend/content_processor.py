import re
from sentence_transformers import SentenceTransformer
from .neo4j_connection import neo4j_conn

class ContentToGraphProcessor:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Nestlé-specific entities for extraction
        self.nestle_products = [
            "KitKat", "Smarties", "Aero", "Quality Street", "Butterfinger",
            "Coffee-mate", "Carnation", "Nespresso", "Gerber"
        ]
        
        self.nestle_categories = [
            "Chocolate", "Confectionery", "Coffee", "Beverages", "Dairy", 
            "Nutrition", "Baby Food", "Hot Chocolate"
        ]
        
        self.sustainability_topics = [
            "Sustainability", "Cocoa Plan", "Water Stewardship", 
            "Carbon Footprint", "Responsible Sourcing"
        ]
    
    def extract_entities(self, text):
        """Extract entities from text content"""
        entities = {
            'products': [],
            'categories': [],
            'topics': [],
            'keywords': []
        }
        
        text_lower = text.lower()
        
        # Extract products
        for product in self.nestle_products:
            if product.lower() in text_lower:
                entities['products'].append(product)
        
        # Extract categories
        for category in self.nestle_categories:
            if category.lower() in text_lower:
                entities['categories'].append(category)
        
        # Extract sustainability topics
        for topic in self.sustainability_topics:
            if topic.lower() in text_lower:
                entities['topics'].append(topic)
        
        # Extract keywords (simple approach - can be enhanced with NLP)
        words = re.findall(r'\b\w{4,}\b', text)
        important_words = [word for word in words if len(word) > 4][:10]
        entities['keywords'] = important_words
        
        return entities
    
    def create_document_node(self, url, title, content, metadata=None):
        """Create a document node in Neo4j"""
        
        # Generate embedding for content
        content_embedding = self.model.encode(content[:500]).tolist()
        
        with neo4j_conn.get_session() as session:
            # Create document node
            doc_query = """
            MERGE (d:Document {url: $url})
            SET d.title = $title,
                d.content = $content,
                d.embedding = $embedding,
                d.created_at = datetime(),
                d.word_count = $word_count
            RETURN d
            """
            
            session.run(doc_query, {
                'url': url,
                'title': title,
                'content': content,
                'embedding': content_embedding,
                'word_count': len(content.split())
            })
            
            # Extract and link entities
            entities = self.extract_entities(content)
            
            # Create product nodes and relationships
            for product in entities['products']:
                self._create_product_relationship(session, url, product)
            
            # Create category nodes and relationships
            for category in entities['categories']:
                self._create_category_relationship(session, url, category)
            
            # Create topic nodes and relationships
            for topic in entities['topics']:
                self._create_topic_relationship(session, url, topic)
            
            # Create keyword nodes and relationships
            for keyword in entities['keywords']:
                self._create_keyword_relationship(session, url, keyword)
    
    def _create_product_relationship(self, session, doc_url, product_name):
        """Create product node and link to document"""
        query = """
        MATCH (d:Document {url: $doc_url})
        MERGE (p:Product {name: $product_name})
        MERGE (d)-[:MENTIONS]->(p)
        """
        session.run(query, {'doc_url': doc_url, 'product_name': product_name})
    
    def _create_category_relationship(self, session, doc_url, category_name):
        """Create category node and link to document"""
        query = """
        MATCH (d:Document {url: $doc_url})
        MERGE (c:Category {name: $category_name})
        MERGE (d)-[:MENTIONS]->(c)
        """
        session.run(query, {'doc_url': doc_url, 'category_name': category_name})
    
    def _create_topic_relationship(self, session, doc_url, topic_name):
        """Create topic node and link to document"""
        query = """
        MATCH (d:Document {url: $doc_url})
        MERGE (t:Topic {name: $topic_name})
        MERGE (d)-[:MENTIONS]->(t)
        """
        session.run(query, {'doc_url': doc_url, 'topic_name': topic_name})
    
    def _create_keyword_relationship(self, session, doc_url, keyword):
        """Create keyword node and link to document"""
        query = """
        MATCH (d:Document {url: $doc_url})
        MERGE (k:Keyword {text: $keyword})
        MERGE (d)-[:CONTAINS]->(k)
        """
        session.run(query, {'doc_url': doc_url, 'keyword': keyword})

processor = ContentToGraphProcessor()