# app.py - Smart Intent Analysis - Fixed Nestlé Chatbot

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import uvicorn
from dotenv import load_dotenv
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

# Load environment variables
load_dotenv()

app = FastAPI(title="Nestlé AI Chatbot", version="2.0.0")

# Global variables
neo4j_available = False
system_ready = False

class Query(BaseModel):
    question: str

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    global neo4j_available, system_ready
    
    print("🚀 Starting Smart Nestlé AI Chatbot...")
    print("="*60)
    
    try:
        from backend.neo4j_connection import neo4j_conn
        if neo4j_conn.connect():
            neo4j_available = True
            print("✅ Neo4j connection successful")
            
            with neo4j_conn.get_session() as session:
                result = session.run("MATCH (n) RETURN count(n) as count")
                count = result.single()['count']
                print(f"📊 Found {count} nodes in Neo4j")
        else:
            print("❌ Neo4j connection failed")
    except Exception as e:
        print(f"❌ Neo4j error: {e}")
    
    system_ready = True
    print("✅ Smart intent system ready!")
    print("="*60)

@app.get("/health")
def health_check():
    return {
        "status": "healthy" if system_ready else "starting",
        "neo4j_available": neo4j_available,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/chat")
async def chat(query: Query):
    """Main chat endpoint with smart intent analysis"""
    
    print(f"\n[Chat] Question: '{query.question}'")
    
    if not system_ready:
        return create_response("System is starting up. Please wait a moment.", [])
    
    try:
        # Analyze the query with improved intent detection
        intent_analysis = analyze_smart_intent(query.question)
        print(f"[Intent] {intent_analysis['intent']} | Entity: {intent_analysis['entity']} | Specific: {intent_analysis['specific_request']}")
        
        if neo4j_available:
            return await process_smart_query(query.question, intent_analysis)
        else:
            return create_fallback_response(query.question, intent_analysis)
            
    except Exception as e:
        print(f"[Error] {e}")
        return create_response("I encountered an error. Let me provide some general information about Nestlé Canada.", get_sources())

def analyze_smart_intent(query: str) -> Dict[str, Any]:
    """Advanced intent analysis that understands natural language"""
    
    query_lower = query.lower().strip()
    
    # Extract entities (products) first
    entity = extract_main_entity(query_lower)
    
    # Detailed intent patterns with specific requests
    intent_patterns = {
        'nutrition': {
            'patterns': [
                r'\b(calories?|nutrition|nutritional|nutrients?)\b',
                r'\b(protein|fat|carbs?|carbohydrates?|sugar|sodium)\b',
                r'\b(healthy|health|diet|dietary)\b',
                r'\bhow many (calories?|carbs?)\b',
                r'\bwhat.*nutrition',
                r'\bnutrition.*info',
                r'\bhow much (protein|fat|sugar)\b'
            ],
            'specific_requests': [
                'calories', 'protein', 'fat', 'carbohydrates', 'sugar', 'sodium', 'nutrition'
            ]
        },
        'availability': {
            'patterns': [
                r'\b(where|how).*(buy|find|get|purchase)\b',
                r'\b(store|shop|retail|available|sell)\b',
                r'\bcan i (buy|find|get)\b',
                r'\bwhere to (buy|find|get)\b',
                r'\b(location|stores?|shops?)\b'
            ],
            'specific_requests': [
                'store locations', 'where to buy', 'availability', 'retailers'
            ]
        },
        'ceo': {
            'patterns': [
                r'\b(ceo|chief executive|president|boss|leader)\b',
                r'\bwho (runs?|leads?|manages?|is in charge)\b',
                r'\bwho.*ceo',
                r'\bmark schneider\b',
                r'\bleadership\b'
            ],
            'specific_requests': [
                'CEO name', 'leadership', 'company head'
            ]
        },
        'ingredients': {
            'patterns': [
                r'\b(ingredients?|made of|contains?|composition)\b',
                r'\bwhat.*made',
                r'\bwhat.*in\b',
                r'\blist.*ingredients?'
            ],
            'specific_requests': [
                'ingredients list', 'composition', 'what contains'
            ]
        },
        'product_info': {
            'patterns': [
                r'\b(tell me about|describe|what is|information about)\b',
                r'\b(details?|info|facts?)\b',
                r'\b(launched|history|when.*made)\b'
            ],
            'specific_requests': [
                'product description', 'history', 'general info'
            ]
        },
        'company': {
            'patterns': [
                r'\b(company|business|about nestlé|nestlé canada)\b',
                r'\b(founded|history|mission)\b',
                r'\b(headquarters|office)\b'
            ],
            'specific_requests': [
                'company info', 'history', 'mission'
            ]
        },
        'sustainability': {
            'patterns': [
                r'\b(sustainability|sustainable|environment|green|eco)\b',
                r'\b(cocoa plan|climate|carbon|recycl)\b'
            ],
            'specific_requests': [
                'sustainability practices', 'environmental impact'
            ]
        },
        'recipe': {
            'patterns': [
                r'\b(recipe|recipes?|cooking|baking|cook|bake)\b',
                r'\b(how to make|how do i make|preparation)\b',
                r'\b(cake|cookies?|dessert|treat)\b',
                r'\bhealthy.*recipe\b',
                r'\brecipe.*for\b'
            ],
            'specific_requests': [
                'recipe instructions', 'cooking method', 'ingredients'
            ]
        },
        'seasonal': {
            'patterns': [
                r'\b(christmas|holiday|gift|gifts?|present)\b',
                r'\b(seasonal|festive|celebration|party)\b',
                r'\b(gift ideas?|present ideas?|holiday treats?)\b',
                r'\b(advent|valentine|easter)\b',
                r'\bwhat.*for christmas\b'
            ],
            'specific_requests': [
                'gift suggestions', 'holiday products', 'seasonal items'
            ]
        }
    }
    
    # Analyze intent
    best_intent = 'general'
    best_score = 0
    specific_request = None
    
    for intent, config in intent_patterns.items():
        score = 0
        
        # Check patterns
        for pattern in config['patterns']:
            if re.search(pattern, query_lower):
                score += 1
        
        # Higher score for more specific matches
        if score > best_score:
            best_score = score
            best_intent = intent
            
            # Identify specific request
            for request in config['specific_requests']:
                if any(word in query_lower for word in request.split()):
                    specific_request = request
                    break
    
    return {
        'intent': best_intent,
        'entity': entity,
        'specific_request': specific_request,
        'confidence': min(best_score / 3.0, 1.0),
        'original_query': query
    }

def extract_main_entity(query_lower: str) -> Optional[str]:
    """Extract the main product entity from query"""
    
    products = {
        'kitkat': 'KitKat',
        'kit kat': 'KitKat', 
        'smarties': 'Smarties',
        'aero': 'Aero',
        'coffee-mate': 'Coffee-mate',
        'coffee mate': 'Coffee-mate',
        'coffeemate': 'Coffee-mate',
        'milo': 'MILO',
        'quality street': 'Quality Street',
        'nido': 'NIDO',
        'garden gourmet': 'Garden Gourmet'
    }
    
    for product_key, product_name in products.items():
        if product_key in query_lower:
            return product_name
    
    return None

async def process_smart_query(query: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Process query with smart routing based on intent"""
    
    from backend.neo4j_connection import neo4j_conn
    
    intent = intent_analysis['intent']
    entity = intent_analysis['entity']
    specific_request = intent_analysis['specific_request']
    
    try:
        with neo4j_conn.get_session() as session:
            
            # Route to specific handlers based on intent
            if intent == 'nutrition' and entity:
                answer = handle_nutrition_query(session, entity, specific_request)
            
            elif intent == 'availability':
                answer = handle_availability_query(session, entity or "Nestlé products")
            
            elif intent == 'ceo':
                answer = handle_ceo_query(session)
            
            elif intent == 'ingredients' and entity:
                answer = handle_ingredients_query(session, entity)
            
            elif intent == 'product_info' and entity:
                answer = handle_product_info_query(session, entity)
            
            elif intent == 'company':
                answer = handle_company_query(session)
            
            elif intent == 'sustainability':
                answer = handle_sustainability_query(session)
            
            elif intent == 'recipe':
                answer = handle_recipe_query(session, query, entity)
            
            elif intent == 'seasonal':
                answer = handle_seasonal_query(session, query)
            
            else:
                # General query or fallback
                answer = handle_general_query(session, entity, query)
            
            if answer:
                return create_response(answer, get_sources(), {
                    "intent": intent,
                    "entity": entity,
                    "specific_request": specific_request,
                    "confidence": intent_analysis['confidence']
                })
            else:
                return create_fallback_response(query, intent_analysis)
    
    except Exception as e:
        print(f"[Query Error] {e}")
        return create_fallback_response(query, intent_analysis)

def handle_nutrition_query(session, product: str, specific_request: str) -> str:
    """Handle specific nutrition questions"""
    
    query = f"""
    MATCH (p:Product {{name: $product}})-[:HAS_NUTRITION]->(n:Nutrition)
    RETURN n
    """
    
    result = session.run(query, {'product': product})
    record = result.single()
    
    if record and record['n']:
        nutrition = record['n']
        
        # Specific nutrition requests
        if specific_request and 'calories' in specific_request:
            if 'calories' in nutrition:
                return f"**{product}** contains **{nutrition['calories']} calories** per {nutrition.get('serving_size', 'serving')}."
            else:
                return f"Calorie information for {product} is not available in my database."
        
        # Full nutrition info
        answer = f"**{product} Nutrition Information:**\n\n"
        
        if 'serving_size' in nutrition:
            answer += f"**Serving Size:** {nutrition['serving_size']}\n\n"
        
        nutritional_facts = []
        if 'calories' in nutrition:
            nutritional_facts.append(f"🔥 **Calories:** {nutrition['calories']}")
        if 'protein' in nutrition:
            nutritional_facts.append(f"💪 **Protein:** {nutrition['protein']}")
        if 'fat' in nutrition:
            nutritional_facts.append(f"🥑 **Fat:** {nutrition['fat']}")
        if 'carbohydrates' in nutrition:
            nutritional_facts.append(f"🌾 **Carbohydrates:** {nutrition['carbohydrates']}")
        if 'iron' in nutrition:
            nutritional_facts.append(f"⚡ **Iron:** {nutrition['iron']}")
        if 'calcium' in nutrition:
            nutritional_facts.append(f"🦴 **Calcium:** {nutrition['calcium']}")
        
        if nutritional_facts:
            answer += "\n".join(nutritional_facts)
            answer += "\n\n💡 *Part of a balanced diet and active lifestyle.*"
            return answer
    
    return f"I don't have specific nutrition information for {product} in my database. You can find detailed nutrition facts on the product packaging or at madewithnestle.ca."

def handle_availability_query(session, product: str) -> str:
    """Handle where to buy questions"""
    
    query = """
    MATCH (s:Store)
    OPTIONAL MATCH (p:Product)-[:AVAILABLE_AT]->(s) 
    WHERE $product = 'Nestlé products' OR p.name = $product
    RETURN DISTINCT s.name as store, s.type as type, s.locations as locations, s.website as website
    ORDER BY s.name
    """
    
    results = session.run(query, {'product': product})
    stores = list(results)
    
    answer = f"**🛒 Where to buy {product}:**\n\n"
    
    if stores:
        answer += "**🏪 Major Retailers:**\n"
        for store in stores:
            if store['store']:
                answer += f"• **{store['store']}**"
                if store['locations']:
                    answer += f" - {store['locations']}"
                if store['website']:
                    answer += f" | Visit: {store['website']}"
                answer += "\n"
    
    answer += "\n**📍 Additional Locations:**\n"
    answer += "• **Convenience Stores:** 7-Eleven, Circle K, Mac's\n"
    answer += "• **Pharmacies:** Shoppers Drug Mart, Rexall, Jean Coutu\n"
    answer += "• **Gas Stations:** Petro-Canada, Shell, Esso\n"
    answer += f"\n💡 **Tip:** Call ahead to confirm {product} is in stock at your local store!"
    
    return answer

def handle_ceo_query(session) -> str:
    """Handle CEO questions"""
    
    queries = [
        "MATCH (p:Person)-[:CEO_OF]->(c:Company) WHERE toLower(c.name) CONTAINS 'nestlé' RETURN p.name as name, p.role as role, c.name as company",
        "MATCH (p:Person) WHERE toLower(p.name) CONTAINS 'schneider' RETURN p.name as name, p.role as role",
        "MATCH (p:Person) WHERE toLower(p.role) CONTAINS 'ceo' RETURN p.name as name, p.role as role"
    ]
    
    for query in queries:
        result = session.run(query)
        record = result.single()
        if record and record['name']:
            name = record['name']
            role = record.get('role', 'CEO')
            return f"**👨‍💼 {name}** is the {role} of Nestlé globally.\n\nHe leads the world's largest food and beverage company with operations in over 180 countries, committed to our mission of \"Good Food, Good Life.\" Under his leadership, Nestlé continues to focus on nutrition, health, and wellness while driving sustainable business practices."
    
    return "**👨‍💼 Mark Schneider** is the CEO of Nestlé globally, leading the world's largest food and beverage company with operations in over 180 countries."

def handle_ingredients_query(session, product: str) -> str:
    """Handle ingredients questions"""
    
    query = f"""
    MATCH (p:Product {{name: $product}})-[:CONTAINS]->(i:Ingredient)
    RETURN i.name as ingredient
    """
    
    result = session.run(query, {'product': product})
    ingredients = [record['ingredient'] for record in result]
    
    if ingredients:
        answer = f"**🧪 {product} Contains:**\n\n"
        for ingredient in ingredients:
            answer += f"• {ingredient}\n"
        return answer
    
    return f"I don't have specific ingredient information for {product} in my database. Please check the product packaging for complete ingredient list."

def handle_product_info_query(session, product: str) -> str:
    """Handle general product information"""
    
    query = """
    MATCH (p:Product {name: $product})
    OPTIONAL MATCH (p)-[:BELONGS_TO]->(c:Category)
    RETURN p, c.name as category
    """
    
    result = session.run(query, {'product': product})
    record = result.single()
    
    if record and record['p']:
        product_data = record['p']
        category = record.get('category', 'Product')
        
        answer = f"**🍫 {product}**\n\n"
        
        if 'description' in product_data:
            answer += f"{product_data['description']}\n\n"
        
        if 'tagline' in product_data:
            answer += f"*\"{product_data['tagline']}\"*\n\n"
        
        details = []
        if 'launched' in product_data:
            details.append(f"**📅 Launched:** {product_data['launched']}")
        
        if 'varieties' in product_data and product_data['varieties']:
            varieties = product_data['varieties'] if isinstance(product_data['varieties'], list) else [product_data['varieties']]
            details.append(f"**🎨 Varieties:** {', '.join(varieties)}")
        
        if 'allergens' in product_data and product_data['allergens']:
            allergens = product_data['allergens'] if isinstance(product_data['allergens'], list) else [product_data['allergens']]
            details.append(f"**⚠️ Allergens:** {', '.join(allergens)}")
        
        if details:
            answer += "\n".join(details)
        
        return answer
    
    return f"I don't have detailed information about {product} in my database."

def handle_company_query(session) -> str:
    """Handle company information questions"""
    
    query = "MATCH (c:Company) WHERE c.name CONTAINS 'Nestlé' RETURN c ORDER BY c.name"
    result = session.run(query)
    companies = list(result)
    
    if companies:
        answer = "**🏢 About Nestlé:**\n\n"
        for record in companies:
            company = record['c']
            name = company.get('name', 'Nestlé')
            
            answer += f"**{name}**\n"
            if 'description' in company:
                answer += f"{company['description']}\n\n"
            
            if 'founded' in company:
                answer += f"📅 **Founded:** {company['founded']}\n"
            if 'headquarters' in company:
                answer += f"🏢 **Headquarters:** {company['headquarters']}\n"
            if 'mission' in company:
                answer += f"🎯 **Mission:** {company['mission']}\n"
            
            answer += "\n"
        
        return answer.strip()
    
    return "**🏢 Nestlé Canada** is a leading food and beverage company with over 100 years of history in Canada, committed to \"Good Food, Good Life.\""

def handle_sustainability_query(session) -> str:
    """Handle sustainability questions"""
    
    query = """
    MATCH (t:Topic)
    WHERE toLower(t.name) CONTAINS 'sustainability' 
       OR toLower(t.name) CONTAINS 'cocoa'
       OR toLower(t.name) CONTAINS 'environment'
    RETURN t
    """
    
    result = session.run(query)
    topics = list(result)
    
    if topics:
        answer = "**🌱 Nestlé Sustainability Commitments:**\n\n"
        for record in topics:
            topic = record['t']
            name = topic.get('name', 'Sustainability')
            
            answer += f"**{name}**\n"
            if 'description' in topic:
                answer += f"{topic['description']}\n"
            
            if 'goals' in topic and topic['goals']:
                goals = topic['goals'] if isinstance(topic['goals'], list) else [topic['goals']]
                answer += f"Goals: {', '.join(goals)}\n"
            
            answer += "\n"
        
        return answer.strip()
    
    return "**🌱 Nestlé is committed to sustainability** through responsible sourcing, environmental stewardship, and supporting farming communities worldwide."

def handle_recipe_query(session, query: str, entity: str) -> str:
    """Handle recipe questions"""
    
    query_lower = query.lower()
    
    # Query recipe documents from Neo4j
    recipe_query = """
    MATCH (d:Document)
    WHERE d.type = 'Recipe' OR toLower(d.title) CONTAINS 'recipe'
    OPTIONAL MATCH (d)-[:USES_INGREDIENT]->(i:Ingredient)
    RETURN d.title as title, d.url as url, collect(i.name) as ingredients
    ORDER BY d.title
    LIMIT 5
    """
    
    results = session.run(recipe_query)
    recipes = list(results)
    
    if recipes:
        answer = "**🍰 Nestlé Recipe Suggestions:**\n\n"
        
        # Check for specific recipe types
        if any(word in query_lower for word in ['healthy', 'health', 'nutritious']):
            answer += "Here are some healthy recipe ideas using Nestlé products:\n\n"
        elif any(word in query_lower for word in ['cake', 'dessert', 'sweet']):
            answer += "Here are some delicious cake and dessert recipes:\n\n"
        elif any(word in query_lower for word in ['christmas', 'holiday', 'festive']):
            answer += "Here are some festive holiday recipes:\n\n"
        else:
            answer += "Here are some popular recipes using Nestlé products:\n\n"
        
        for recipe in recipes:
            title = recipe['title']
            url = recipe.get('url', '')
            ingredients = recipe.get('ingredients', [])
            
            answer += f"**{title}**\n"
            
            # Add ingredients if available
            if ingredients and len(ingredients) > 0:
                key_ingredients = [ing for ing in ingredients if ing][:4]  # Show first 4 ingredients
                if key_ingredients:
                    answer += f"*Key ingredients: {', '.join(key_ingredients)}*\n"
            
            # Add URL if available
            if url:
                answer += f"📖 Full recipe: {url}\n"
            
            answer += "\n"
        
        answer += "💡 **Visit madewithnestle.ca/recipes for more delicious recipe ideas!**"
        return answer
    
    else:
        # Fallback recipe suggestions based on products
        if any(word in query_lower for word in ['healthy', 'health']):
            return """**🥗 Healthy Recipe Ideas with Nestlé Products:**

**BOOST Just Hidden Zucchini Cake**
*A nutritious cake that sneaks in vegetables!*
• Key ingredients: BOOST powder, zucchini, whole wheat flour
• Perfect for: Healthy desserts, kids' snacks

**MILO Energy Balls**
*No-bake energy treats packed with nutrients*
• Key ingredients: MILO powder, oats, peanut butter, honey
• Perfect for: Pre-workout snacks, lunchbox treats

**NIDO Mango Smoothie Bowl**
*Creamy, protein-rich breakfast*
• Key ingredients: NIDO milk powder, fresh mango, granola
• Perfect for: Healthy breakfast, post-workout recovery

💡 **Visit madewithnestle.ca/recipes for complete instructions and more healthy recipe ideas!**"""
        
        elif any(word in query_lower for word in ['christmas', 'holiday', 'gift']):
            return """**🎄 Holiday Recipe & Gift Ideas:**

**Christmas Treats:**
• **Quality Street Advent Calendar** - Perfect countdown to Christmas
• **KitKat Holiday Mix** - Festive chocolate assortment
• **Smarties Cookie Decorating** - Fun family activity

**Holiday Baking Ideas:**
• **Aero Chocolate Bark** - Easy holiday dessert
• **Coffee-mate Holiday Latte** - Warm festive drinks
• **KitKat Chocolate Cake** - Perfect for holiday parties

**Gift Ideas:**
• Premium chocolate gift boxes
• Holiday-themed product bundles
• Homemade treats using Nestlé products

💡 **Visit madewithnestle.ca for complete holiday recipes and gift inspiration!**"""
        
        else:
            return """**👩‍🍳 Popular Nestlé Recipes:**

**Sweet Treats:**
• **KitKat Chocolate Cake** - Decadent dessert with crushed KitKat
• **Smarties Cookies** - Colorful cookies kids love
• **Aero Chocolate Mousse** - Light and airy dessert

**Healthy Options:**
• **MILO Energy Balls** - No-bake nutritious snacks
• **BOOST Protein Smoothie** - Post-workout nutrition
• **NIDO Fruit Parfait** - Calcium-rich breakfast

**Beverages:**
• **Coffee-mate Specialty Drinks** - Gourmet coffee creations
• **MILO Hot Chocolate** - Comforting winter drink

💡 **Visit madewithnestle.ca/recipes for complete instructions and video tutorials!**"""

def handle_seasonal_query(session, query: str) -> str:
    """Handle seasonal and gift questions"""
    
    query_lower = query.lower()
    
    # Query seasonal campaigns and products
    seasonal_query = """
    MATCH (c:Campaign)
    OPTIONAL MATCH (p:Product)-[:FEATURED_IN]->(c)
    RETURN c.name as campaign, c.theme as theme, c.start_date as start_date, c.end_date as end_date, collect(p.name) as products
    ORDER BY c.start_date DESC
    """
    
    results = session.run(seasonal_query)
    campaigns = list(results)
    
    if campaigns:
        answer = ""
        
        # Check for Christmas/Holiday queries
        if any(word in query_lower for word in ['christmas', 'holiday', 'gift', 'present']):
            answer = "**🎄 Christmas & Holiday Gift Ideas from Nestlé:**\n\n"
            
            # Find Christmas campaigns
            christmas_campaigns = [c for c in campaigns if 'christmas' in c['campaign'].lower() or 'holiday' in c.get('theme', '').lower()]
            
            if christmas_campaigns:
                for campaign in christmas_campaigns:
                    answer += f"**{campaign['campaign']}**\n"
                    if campaign.get('theme'):
                        answer += f"*Theme: {campaign['theme']}*\n"
                    
                    products = campaign.get('products', [])
                    if products:
                        answer += "Featured products:\n"
                        for product in products:
                            if product:
                                answer += f"• {product}\n"
                    answer += "\n"
            
            # Add general Christmas gift suggestions
            answer += "**🎁 Perfect Christmas Gifts:**\n\n"
            answer += "**For Chocolate Lovers:**\n"
            answer += "• **Quality Street** - Classic Christmas chocolates\n"
            answer += "• **KitKat Holiday Collection** - Festive packaging\n"
            answer += "• **Aero Gift Sets** - Light, bubbly treats\n\n"
            
            answer += "**For Coffee Enthusiasts:**\n"
            answer += "• **Coffee-mate Holiday Flavors** - Pumpkin Spice, Gingerbread\n"
            answer += "• **Premium Coffee Gift Sets**\n\n"
            
            answer += "**For Families:**\n"
            answer += "• **Smarties Advent Calendar** - Daily treats for kids\n"
            answer += "• **Holiday Baking Kits** - Fun family activities\n\n"
            
            answer += "**For Health-Conscious Friends:**\n"
            answer += "• **MILO Gift Sets** - Nutritious energy drinks\n"
            answer += "• **BOOST Protein Products** - Healthy nutrition\n\n"
            
            answer += "💡 **Visit your local retailer or madewithnestle.ca for holiday gift bundles!**"
            
        else:
            # General seasonal information
            answer = "**🗓️ Nestlé Seasonal Campaigns:**\n\n"
            
            for campaign in campaigns[:3]:  # Show top 3 campaigns
                answer += f"**{campaign['campaign']}**\n"
                if campaign.get('theme'):
                    answer += f"Theme: {campaign['theme']}\n"
                
                products = campaign.get('products', [])
                if products:
                    answer += f"Featured products: {', '.join([p for p in products if p][:3])}\n"
                answer += "\n"
        
        return answer
    
    else:
        # Fallback seasonal suggestions
        if any(word in query_lower for word in ['christmas', 'holiday', 'gift']):
            return """**🎄 Christmas Gift Ideas from Nestlé:**

**🍫 Chocolate Gifts:**
• **Quality Street** - Traditional Christmas chocolates
• **KitKat Holiday Edition** - Special festive packaging
• **Aero Mint** - Refreshing holiday treat
• **Smarties** - Colorful fun for kids

**☕ Holiday Beverages:**
• **Coffee-mate Holiday Flavors** - Pumpkin Spice, Gingerbread
• **MILO Hot Chocolate** - Warm winter comfort
• **Premium Coffee Collections**

**🎁 Gift Bundle Ideas:**
• **Family Treat Box** - Mix of chocolates and snacks
• **Baking Kit** - Products for holiday cookie making
• **Coffee Lover's Set** - Coffee-mate flavors + premium coffee

**🏪 Where to Find:**
Available at Walmart, Loblaws, Metro, Sobeys, and specialty gift shops across Canada.

💡 **Perfect for stocking stuffers, office gifts, and family treats!**"""
        
        else:
            return """**🗓️ Nestlé Seasonal Offerings:**

**🎃 Fall/Autumn:**
• Pumpkin Spice Coffee-mate
• Back-to-school MILO promotions
• Halloween candy varieties

**❄️ Winter/Christmas:**
• Holiday-themed packaging
• Gift sets and bundles
• Seasonal flavors

**🌸 Spring/Easter:**
• Easter chocolate shapes
• Pastel-colored Smarties
• Spring baking ingredients

**☀️ Summer:**
• Refreshing iced coffee recipes
• Summer camp snack packs
• Outdoor adventure nutrition

💡 **Each season brings special promotions and limited-edition products!**"""

def handle_general_query(session, entity: str, query: str) -> str:
    """Handle general queries"""
    
    if entity:
        # Try to find any information about the entity
        cypher_query = """
        MATCH (n)
        WHERE n.name = $entity
        RETURN n, labels(n) as labels
        """
        
        result = session.run(cypher_query, {'entity': entity})
        record = result.single()
        
        if record:
            node = record['n']
            node_type = record['labels'][0] if record['labels'] else 'Item'
            
            answer = f"**{entity}** ({node_type})\n\n"
            if 'description' in node:
                answer += f"{node['description']}\n\n"
            
            return answer
    
    # Default response
    return get_default_info()

def get_default_info() -> str:
    """Default company information"""
    return """**🏠 Welcome to Nestlé Canada!**

We're a leading food and beverage company with over 100 years of history in Canada. Our mission is "Good Food, Good Life."

**🍫 Popular Products:**
• **KitKat** - "Have a break, have a KitKat!"
• **Smarties** - Colorful chocolate candies
• **Aero** - Light, bubbly chocolate
• **Coffee-mate** - Premium coffee creamer

**👨‍💼 Leadership:** Mark Schneider serves as CEO globally

**🎯 Ask me about:**
• Product nutrition and ingredients
• Where to buy our products  
• Company information and values
• Sustainability initiatives

*Try asking: "What calories are in KitKat?" or "Where can I buy Smarties?"*"""

def create_response(answer: str, sources: List[str], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create standardized response"""
    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            **(metadata or {}),
            "timestamp": datetime.now().isoformat(),
            "processing_method": "Smart Intent Analysis"
        }
    }

def create_fallback_response(query: str, intent_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Create fallback response"""
    return create_response(
        f"I understand you're asking about {intent_analysis.get('entity', 'Nestlé products')}, but I don't have specific information in my database. " + get_default_info(),
        get_sources(),
        {"fallback": True, "intent": intent_analysis.get('intent', 'unknown')}
    )

def get_sources() -> List[str]:
    """Get source URLs"""
    return [
        "https://www.madewithnestle.ca",
        "https://corporate.nestle.ca"
    ]

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def get_chat_ui():
    return FileResponse(os.path.join("frontend", "index.html"))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting Smart Intent Nestlé Chatbot on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)