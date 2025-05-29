# backend/graphrag_system.py - Clean GraphRAG System Implementation

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from .neo4j_connection import neo4j_conn
from .graph_schema import schema_manager
from .intent_analyzer import IntentAnalyzer
from .context_retriever import ContextRetriever
from .ai_response_generator import AIResponseGenerator
from .web_source_manager import WebSourceManager
from .neo4j_data_initializer import data_initializer

class GraphRAGSystem:
    """Main GraphRAG system that coordinates all components"""
    
    def __init__(self):
        self.intent_analyzer = None
        self.context_retriever = None
        self.ai_generator = None
        self.web_manager = None
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all GraphRAG components"""
        try:
            print("🔧 Initializing GraphRAG system...")
            
            # Test Neo4j connection
            if not neo4j_conn.connect():
                print("❌ Failed to connect to Neo4j")
                return False
            
            # Setup schema
            schema_manager.setup_schema()
            
            # Check if data exists, if not, initialize it
            await self._ensure_data_exists()
            
            # Initialize components
            self.intent_analyzer = IntentAnalyzer()
            self.context_retriever = ContextRetriever()
            self.ai_generator = AIResponseGenerator()
            self.web_manager = WebSourceManager()
            
            self.is_initialized = True
            print("✅ GraphRAG system initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ GraphRAG initialization failed: {e}")
            return False
    
    async def _ensure_data_exists(self):
        """Ensure Neo4j has data, enhance if needed"""
        try:
            with neo4j_conn.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()['count']
                
                if count == 0:
                    print("📊 No data found in Neo4j, initializing...")
                    data_initializer.initialize_data()
                elif count < 10:
                    print(f"📊 Found {count} nodes, enhancing with core entities...")
                    data_initializer.initialize_data()  # Will preserve existing data
                else:
                    print(f"✅ Found {count} nodes in Neo4j - using existing data")
        except Exception as e:
            print(f"⚠️ Error checking data: {e}")
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query through complete GraphRAG pipeline"""
        
        if not self.is_initialized:
            raise Exception("GraphRAG system not initialized")
        
        try:
            # Step 1: Analyze query intent and extract entities
            analysis = await self.intent_analyzer.analyze_query(user_query)
            print(f"[GraphRAG] Intent: {analysis['intent']}, Entities: {analysis['entities']}")
            
            # Step 2: Retrieve relevant context from Neo4j graph
            graph_context = await self.context_retriever.get_relevant_context(
                user_query, 
                analysis['intent'], 
                analysis['entities']
            )
            print(f"[GraphRAG] Retrieved {len(graph_context.get('nodes', []))} relevant graph nodes")
            
            # Step 3: Get web sources for additional context
            web_sources = await self.web_manager.get_relevant_sources(
                user_query, 
                analysis['entities']
            )
            
            # Step 4: Generate AI response using graph context
            ai_response = await self.ai_generator.generate_response(
                user_query=user_query,
                intent=analysis['intent'],
                entities=analysis['entities'],
                graph_context=graph_context,
                web_sources=web_sources
            )
            
            # Step 5: Compile final response
            final_response = {
                "answer": ai_response,
                "sources": web_sources,
                "metadata": {
                    "intent": analysis['intent'],
                    "entities": analysis['entities'],
                    "graph_nodes_used": len(graph_context.get('nodes', [])),
                    "processing_method": "Neo4j GraphRAG",
                    "timestamp": datetime.now().isoformat(),
                    "confidence": analysis.get('confidence', 0.5)
                }
            }
            
            return final_response
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            # Return graceful error response
            return {
                "answer": "I apologize, but I'm having trouble processing your question right now. Please try asking about our products, sustainability initiatives, or company information. You can also visit madewithnestle.ca for comprehensive information.",
                "sources": ["https://www.madewithnestle.ca"],
                "metadata": {
                    "error": str(e),
                    "processing_method": "Error fallback",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def get_graph_stats(self) -> Dict[str, Any]:
        """Get current graph statistics"""
        if not self.is_initialized:
            return {"error": "GraphRAG system not initialized"}
        
        try:
            with neo4j_conn.get_session() as session:
                # Get node counts by type
                node_query = """
                MATCH (n)
                UNWIND labels(n) as label
                WITH label, count(*) as count
                RETURN label, count
                ORDER BY count DESC
                """
                
                node_results = session.run(node_query)
                nodes = {}
                total_nodes = 0
                
                for record in node_results:
                    nodes[record['label']] = record['count']
                    total_nodes += record['count']
                
                # Get relationship counts
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) as relationship_type, count(r) as count
                ORDER BY count DESC
                """
                
                rel_results = session.run(rel_query)
                relationships = {}
                total_relationships = 0
                
                for record in rel_results:
                    relationships[record['relationship_type']] = record['count']
                    total_relationships += record['count']
                
                return {
                    'nodes': nodes,
                    'relationships': relationships,
                    'total_nodes': total_nodes,
                    'total_relationships': total_relationships,
                    'system_status': 'operational',
                    'initialized': self.is_initialized
                }
                
        except Exception as e:
            return {
                'error': f"Failed to get graph stats: {str(e)}",
                'system_status': 'error',
                'initialized': self.is_initialized
            }