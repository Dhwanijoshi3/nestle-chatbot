# backend/enhanced_graphrag_system.py - Hybrid Static + Dynamic GraphRAG System

from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

from .neo4j_connection import neo4j_conn
from .graph_schema import schema_manager
from .intent_analyzer import IntentAnalyzer
from .context_retriever import ContextRetriever
from .ai_response_generator import AIResponseGenerator
from .web_source_manager import WebSourceManager
from .safe_data_enhancer import safe_enhancer
from .realtime_web_scraper import realtime_scraper

class EnhancedGraphRAGSystem:
    """Enhanced GraphRAG system combining static Neo4j data with real-time web scraping"""
    
    def __init__(self):
        self.intent_analyzer = None
        self.context_retriever = None
        self.ai_generator = None
        self.web_manager = None
        self.is_initialized = False
        self.data_enhanced = False
    
    async def initialize(self) -> bool:
        """Initialize the enhanced GraphRAG system"""
        try:
            print("🚀 Initializing Enhanced GraphRAG system...")
            
            # Test Neo4j connection
            if not neo4j_conn.connect():
                print("❌ Failed to connect to Neo4j")
                return False
            
            # Setup schema
            schema_manager.setup_schema()
            
            # Phase 1: Enhance existing data safely
            await self._enhance_static_data()
            
            # Initialize components
            self.intent_analyzer = IntentAnalyzer()
            self.context_retriever = ContextRetriever()
            self.ai_generator = AIResponseGenerator()
            self.web_manager = WebSourceManager()
            
            self.is_initialized = True
            print("✅ Enhanced GraphRAG system initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Enhanced GraphRAG initialization failed: {e}")
            return False
    
    async def _enhance_static_data(self):
        """Phase 1: Safely enhance existing Neo4j data"""
        if not self.data_enhanced:
            print("📊 Phase 1: Enhancing static data...")
            
            try:
                # Run safe data enhancement
                if safe_enhancer.enhance_existing_data():
                    self.data_enhanced = True
                    print("✅ Static data enhancement completed")
                else:
                    print("⚠️ Static data enhancement had issues, continuing anyway")
            except Exception as e:
                print(f"⚠️ Error enhancing static data: {e}")
    
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query through enhanced GraphRAG pipeline (Static + Dynamic)"""
        
        if not self.is_initialized:
            raise Exception("Enhanced GraphRAG system not initialized")
        
        try:
            # Step 1: Analyze query intent and extract entities
            analysis = await self.intent_analyzer.analyze_query(user_query)
            print(f"[Enhanced GraphRAG] Intent: {analysis['intent']}, Entities: {analysis['entities']}")
            
            # Step 2: Get static context from Neo4j (enhanced data)
            static_context = await self.context_retriever.get_relevant_context(
                user_query, 
                analysis['intent'], 
                analysis['entities']
            )
            print(f"[Enhanced GraphRAG] Retrieved {len(static_context.get('nodes', []))} static nodes")
            
            # Step 3: Get dynamic information via web scraping
            dynamic_info = await self._get_dynamic_information(user_query, analysis['intent'], analysis['entities'])
            print(f"[Enhanced GraphRAG] Retrieved dynamic info: {list(dynamic_info.keys())}")
            
            # Step 4: Get web sources
            web_sources = await self.web_manager.get_relevant_sources(
                user_query, 
                analysis['entities']
            )
            
            # Step 5: Combine static and dynamic contexts
            combined_context = self._combine_contexts(static_context, dynamic_info)
            
            # Step 6: Generate enhanced AI response
            ai_response = await self.ai_generator.generate_response(
                user_query=user_query,
                intent=analysis['intent'],
                entities=analysis['entities'],
                graph_context=combined_context,
                web_sources=web_sources
            )
            
            # Step 7: Compile final enhanced response
            final_response = {
                "answer": ai_response,
                "sources": web_sources,
                "metadata": {
                    "intent": analysis['intent'],
                    "entities": analysis['entities'],
                    "static_nodes_used": len(static_context.get('nodes', [])),
                    "dynamic_info_types": list(dynamic_info.keys()),
                    "processing_method": "Enhanced GraphRAG (Static + Dynamic)",
                    "timestamp": datetime.now().isoformat(),
                    "confidence": analysis.get('confidence', 0.5),
                    "data_sources": ["Neo4j Enhanced Database", "Real-time Web Scraping"]
                }
            }
            
            return final_response
            
        except Exception as e:
            print(f"❌ Error in enhanced query processing: {e}")
            # Return graceful error response
            return {
                "answer": "I apologize, but I'm having trouble processing your question right now. However, I can still help with information about our products, sustainability initiatives, or company information. Please try rephrasing your question or visit madewithnestle.ca for comprehensive information.",
                "sources": ["https://www.madewithnestle.ca"],
                "metadata": {
                    "error": str(e),
                    "processing_method": "Enhanced GraphRAG Error Fallback",
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    async def _get_dynamic_information(self, user_query: str, intent: str, entities: List[str]) -> Dict[str, Any]:
        """Phase 2: Get real-time dynamic information"""
        
        # Determine if dynamic information is needed
        needs_dynamic = self._should_get_dynamic_info(user_query, intent)
        
        if not needs_dynamic:
            print("📋 Static data sufficient, skipping web scraping")
            return {}
        
        print("🌐 Phase 2: Getting real-time information...")
        
        try:
            # Get dynamic information via web scraping
            dynamic_info = await realtime_scraper.get_dynamic_information(user_query, intent, entities)
            return dynamic_info
        
        except Exception as e:
            print(f"⚠️ Error getting dynamic info: {e}")
            return {'error': f'Dynamic information unavailable: {str(e)}'}
    
    def _should_get_dynamic_info(self, user_query: str, intent: str) -> bool:
        """Determine if dynamic web scraping is needed"""
        
        query_lower = user_query.lower()
        
        # Always get dynamic info for these cases
        dynamic_triggers = [
            # Availability questions
            'where can i buy', 'where to buy', 'where do i find', 'store locations',
            'available at', 'find in stores', 'purchase', 'buy online',
            
            # Current/recent information
            'what\'s new', 'latest', 'recent', 'current', 'today', 'now',
            'updates', 'news', 'announcement', 'recently',
            
            # Pricing and promotions
            'price', 'cost', 'how much', 'promotion', 'sale', 'discount',
            
            # Real-time availability
            'in stock', 'available now', 'can i get', 'do you have'
        ]
        
        # Intent-based triggers
        intent_triggers = ['availability', 'company_info', 'general_info']
        
        # Check for triggers in query
        for trigger in dynamic_triggers:
            if trigger in query_lower:
                return True
        
        # Check intent
        if intent in intent_triggers:
            return True
        
        return False
    
    def _combine_contexts(self, static_context: Dict[str, Any], dynamic_info: Dict[str, Any]) -> Dict[str, Any]:
        """Combine static Neo4j context with dynamic web-scraped information"""
        
        combined = {
            'nodes': static_context.get('nodes', []),
            'relationships': static_context.get('relationships', []),
            'paths': static_context.get('paths', []),
            'summary': static_context.get('summary', ''),
            'dynamic_info': dynamic_info
        }
        
        # Enhance summary with dynamic information
        if dynamic_info and not dynamic_info.get('error'):
            dynamic_summary_parts = []
            
            if dynamic_info.get('news'):
                dynamic_summary_parts.append(f"Latest news: {len(dynamic_info['news'])} recent updates")
            
            if dynamic_info.get('store_locations'):
                dynamic_summary_parts.append(f"Store availability: {len(dynamic_info['store_locations'])} retailer locations")
            
            if dynamic_info.get('sustainability_updates'):
                dynamic_summary_parts.append(f"Sustainability updates: {len(dynamic_info['sustainability_updates'])} recent initiatives")
            
            if dynamic_summary_parts:
                if combined['summary']:
                    combined['summary'] += "; " + "; ".join(dynamic_summary_parts)
                else:
                    combined['summary'] = "; ".join(dynamic_summary_parts)
        
        return combined
    
    def get_enhanced_graph_stats(self) -> Dict[str, Any]:
        """Get enhanced graph statistics including dynamic capabilities"""
        if not self.is_initialized:
            return {"error": "Enhanced GraphRAG system not initialized"}
        
        try:
            with neo4j_conn.get_session() as session:
                # Get enhanced node counts
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
                    'system_status': 'enhanced_operational',
                    'data_enhanced': self.data_enhanced,
                    'dynamic_scraping_enabled': True,
                    'capabilities': [
                        'Enhanced product information',
                        'Store location data',
                        'Nutritional information',
                        'FAQ database',
                        'Real-time news scraping',
                        'Dynamic availability checking',
                        'Sustainability updates'
                    ],
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'error': f"Failed to get enhanced stats: {str(e)}",
                'system_status': 'error',
                'data_enhanced': self.data_enhanced
            }