# backend/ai_response_generator.py - Updated AI Response Generation

import os
from typing import Dict, List, Any, Optional
from openai import OpenAI

class AIResponseGenerator:
    """Generates AI responses using graph context with modern OpenAI API"""
    
    def __init__(self):
        self.openai_available = self._check_openai()
        if self.openai_available:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def _check_openai(self) -> bool:
        """Check if OpenAI is available"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key.startswith('sk-'):
                return True
            else:
                print("⚠️ OpenAI API key not found or invalid")
                return False
        except Exception as e:
            print(f"⚠️ OpenAI initialization error: {e}")
            return False
    
    async def generate_response(
        self, 
        user_query: str, 
        intent: str, 
        entities: List[str], 
        graph_context: Dict[str, Any], 
        web_sources: List[str]
    ) -> str:
        """Generate AI response using graph context"""
        
        # Format context from graph data
        context_text = self._format_graph_context(graph_context, intent, entities)
        
        if self.openai_available and context_text:
            return await self._generate_openai_response(user_query, context_text, intent, entities, web_sources)
        else:
            return await self._generate_fallback_response(user_query, context_text, intent, entities, web_sources)
    
    def _format_graph_context(self, graph_context: Dict[str, Any], intent: str, entities: List[str]) -> str:
        """Format graph context into readable text"""
        
        nodes = graph_context.get('nodes', [])
        relationships = graph_context.get('relationships', [])
        
        if not nodes:
            return ""
        
        context_parts = []
        
        # Sort nodes by relevance
        direct_matches = [n for n in nodes if n.get('relevance') == 'direct_match']
        related_nodes = [n for n in nodes if n.get('relevance') != 'direct_match']
        
        # Add direct matches first
        for node in direct_matches[:3]:  # Limit to prevent token overflow
            node_info = self._format_node_info(node)
            if node_info:
                context_parts.append(f"**{node['name']}**: {node_info}")
        
        # Add related information
        for node in related_nodes[:3]:  # Limit related nodes
            node_info = self._format_node_info(node)
            if node_info:
                context_parts.append(f"Related - **{node['name']}**: {node_info}")
        
        # Add relationship information if available
        if relationships:
            rel_info = self._format_relationship_info(relationships[:5])  # Limit relationships
            if rel_info:
                context_parts.append(f"Connections: {rel_info}")
        
        return "\n".join(context_parts)
    
    def _format_node_info(self, node: Dict[str, Any]) -> str:
        """Format individual node information"""
        
        properties = node.get('properties', {})
        node_type = node.get('type', 'Unknown')
        
        info_parts = []
        
        # Add description if available
        if 'description' in properties:
            info_parts.append(properties['description'])
        
        # Add type-specific properties
        if node_type == 'Product':
            for key in ['tagline', 'launched', 'varieties']:
                if key in properties:
                    value = properties[key]
                    if isinstance(value, list):
                        info_parts.append(f"{key.title()}: {', '.join(map(str, value[:3]))}")
                    else:
                        info_parts.append(f"{key.title()}: {value}")
        
        elif node_type == 'Company':
            for key in ['founded', 'headquarters', 'mission', 'ceo']:
                if key in properties:
                    info_parts.append(f"{key.title()}: {properties[key]}")
        
        elif node_type == 'Topic':
            for key in ['goals', 'focus_areas', 'commitment']:
                if key in properties:
                    value = properties[key]
                    if isinstance(value, list):
                        info_parts.append(f"{key.replace('_', ' ').title()}: {', '.join(value[:3])}")
                    else:
                        info_parts.append(f"{key.replace('_', ' ').title()}: {value}")
        
        # Join and limit length
        result = ". ".join(info_parts[:3])
        if len(result) > 300:
            result = result[:297] + "..."
        
        return result
    
    def _format_relationship_info(self, relationships: List[Dict[str, Any]]) -> str:
        """Format relationship information"""
        
        rel_descriptions = []
        
        for rel in relationships:
            from_node = rel.get('from', 'Unknown')
            to_node = rel.get('to', 'Unknown')
            rel_type = rel.get('type', 'RELATED_TO')
            
            # Format relationship in readable way
            rel_map = {
                'BELONGS_TO': f"{from_node} belongs to {to_node}",
                'PRODUCED_BY': f"{from_node} is produced by {to_node}",
                'SUPPORTS': f"{from_node} supports {to_node}",
                'USED_FOR': f"{from_node} is used for {to_node}",
                'CEO_OF': f"{from_node} is CEO of {to_node}",
                'COMMITTED_TO': f"{from_node} is committed to {to_node}",
                'SUBSIDIARY_OF': f"{from_node} is a subsidiary of {to_node}"
            }
            
            description = rel_map.get(rel_type, f"{from_node} is related to {to_node}")
            rel_descriptions.append(description)
        
        return "; ".join(rel_descriptions)
    
    async def _generate_openai_response(
        self, 
        user_query: str, 
        context_text: str, 
        intent: str, 
        entities: List[str], 
        web_sources: List[str]
    ) -> str:
        """Generate response using OpenAI"""
        
        try:
            system_prompt = self._create_system_prompt(intent, entities)
            user_prompt = self._create_user_prompt(user_query, context_text, web_sources)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI generation error: {e}")
            return await self._generate_fallback_response(user_query, context_text, intent, entities, web_sources)
    
    async def _generate_fallback_response(
        self, 
        user_query: str, 
        context_text: str, 
        intent: str, 
        entities: List[str], 
        web_sources: List[str]
    ) -> str:
        """Generate structured response when OpenAI is not available"""
        
        query_lower = user_query.lower()
        
        # Special handling for availability questions
        if intent == 'availability' or any(word in query_lower for word in ['where', 'buy', 'purchase', 'find', 'store']):
            product_name = entities[0] if entities else 'Nestlé products'
            
            response = f"**Where to buy {product_name}:**\n\n"
            response += f"{product_name} is available at major retailers across Canada:\n\n"
            response += "**Major Supermarket Chains:**\n"
            response += "• **Walmart** - 400+ locations nationwide (Chocolate aisle, $1.50-$8.99)\n"
            response += "• **Loblaws** - 170+ stores in Ontario & Atlantic Canada\n"
            response += "• **Metro** - 650+ locations in Ontario & Quebec\n"
            response += "• **Sobeys** - 900+ stores nationwide\n\n"
            response += "**Convenience Stores:**\n"
            response += "• 7-Eleven, Circle K, Mac's convenience stores\n\n"
            response += "**Pharmacies:**\n"
            response += "• Shoppers Drug Mart, Rexall, Jean Coutu\n\n"
            response += f"**Store Locator Tips:**\n"
            response += f"• Visit walmart.ca, loblaws.ca, or metro.ca store locators\n"
            response += f"• {product_name} is typically found in the chocolate or candy aisle\n"
            response += f"• Call ahead to confirm {product_name} availability at your local store"
            
        # Special handling for CEO questions
        elif intent == 'company_info' and any(word in query_lower for word in ['ceo', 'runs', 'leads', 'chief', 'boss']):
            if 'mark schneider' in context_text.lower():
                response = "Based on our knowledge base:\n\n**Mark Schneider** is the CEO of Nestlé, the global parent company of Nestlé Canada."
            else:
                response = "Based on our knowledge base:\n\nMark Schneider serves as the Chief Executive Officer of Nestlé globally. Nestlé Canada operates as a subsidiary of the global Nestlé company."
        elif context_text:
            response = f"Based on our knowledge base:\n\n{context_text}"
        else:
            response = "I'd be happy to help you with information about Nestlé Canada."
        
        # Add intent-specific guidance
        if intent == 'product_info' and entities:
            entity_text = ", ".join(entities)
            response += f"\n\nFor more detailed information about {entity_text}, including nutritional facts and availability, please visit madewithnestle.ca."
        
        elif intent == 'company_info':
            response += "\n\nFor comprehensive company information, leadership details, and corporate updates, visit corporate.nestle.ca."
        
        elif intent == 'sustainability':
            response += "\n\nYou can learn more about our sustainability commitments and progress at madewithnestle.ca/sustainability."
        
        elif intent == 'availability':
            response += "\n\nFor the most current store locations and product availability, visit the retailer websites or use their store locator tools."
        
        # Add general closing
        response += "\n\nIs there anything specific you'd like to know more about?"
        
        return response
    
    def _create_system_prompt(self, intent: str, entities: List[str]) -> str:
        """Create system prompt for OpenAI"""
        
        leadership_context = ""
        if intent == 'company_info' and any(word in ' '.join(entities + [intent]).lower() for word in ['ceo', 'runs', 'leader', 'boss', 'chief']):
            leadership_context = """
IMPORTANT: When answering questions about leadership, CEO, or "who runs" the company:
- Nestlé global CEO is Mark Schneider
- Nestlé Canada is a subsidiary of the global Nestlé company
- Always mention the global leadership when asked about "who runs Nestlé" or "who is the CEO"
"""

        return f"""You are a knowledgeable and friendly AI assistant for Nestlé Canada. You help customers learn about Nestlé products, company information, sustainability efforts, and more.

GUIDELINES:
1. Use ONLY the information provided in the context - do not add information not given
2. Be conversational, helpful, and maintain Nestlé's "Good Food, Good Life" spirit
3. If the context doesn't fully answer the question, acknowledge this and suggest visiting madewithnestle.ca
4. Keep responses informative but concise (2-4 paragraphs maximum)
5. Always be accurate and never make up information
6. Focus on being helpful and customer-oriented

{leadership_context}

CURRENT QUERY CONTEXT:
- Intent: {intent}
- Mentioned entities: {', '.join(entities) if entities else 'None'}

Respond naturally and helpfully based on the provided context. If information is missing, guide users to appropriate resources."""
    
    def _create_user_prompt(self, user_query: str, context_text: str, web_sources: List[str]) -> str:
        """Create user prompt for OpenAI"""
        
        prompt = f"""Customer Question: {user_query}

Available Information from Knowledge Base:
{context_text if context_text else "No specific information found in knowledge base."}

Additional Resources Available:
{chr(10).join([f"- {source}" for source in web_sources]) if web_sources else "- madewithnestle.ca"}

Please provide a helpful and accurate response using the available information. If the information doesn't fully answer the question, acknowledge what you can share and suggest where they can find more complete information."""
        
        return prompt