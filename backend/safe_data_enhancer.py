# backend/safe_data_enhancer.py - Safe Data Enhancement Without Duplicates

from .neo4j_connection import neo4j_conn
from datetime import datetime

class SafeDataEnhancer:
    """Safely enhances Neo4j data without creating duplicates"""
    
    def __init__(self):
        pass
    
    def enhance_existing_data(self):
        """Master function to safely enhance existing data"""
        print("🔒 Starting SAFE data enhancement (no duplicates)...")
        
        try:
            with neo4j_conn.get_session() as session:
                # Step 1: Analyze what exists
                existing_data = self._analyze_existing_data(session)
                print(f"📊 Found existing data: {existing_data}")
                
                # Step 2: Only add missing information
                self._safely_enhance_products(session)
                self._safely_add_store_framework(session)
                self._safely_add_nutrition_data(session)
                self._safely_enhance_sustainability(session)
                self._safely_add_faq_framework(session)
                
                print("✅ Safe data enhancement completed!")
                return True
                
        except Exception as e:
            print(f"❌ Error in safe enhancement: {e}")
            return False
    
    def _analyze_existing_data(self, session):
        """Analyze what data already exists"""
        analysis_query = """
        // Get overview of existing data
        MATCH (n)
        WITH labels(n) as nodeType, count(*) as count
        UNWIND nodeType as label
        WITH label, sum(count) as total
        RETURN label, total
        ORDER BY total DESC
        """
        
        result = session.run(analysis_query)
        existing_data = {}
        for record in result:
            existing_data[record['label']] = record['total']
        
        return existing_data
    
    def _safely_enhance_products(self, session):
        """Safely enhance existing products without duplicates"""
        print("📦 Safely enhancing product information...")
        
        enhancement_query = """
        // Enhance KitKat (your existing product)
        MERGE (kitkat:Product {name: "KitKat"})
        SET kitkat.tagline = COALESCE(kitkat.tagline, "Have a break, have a KitKat"),
            kitkat.target_audience = COALESCE(kitkat.target_audience, "Adults and teenagers"),
            kitkat.available_sizes = COALESCE(kitkat.available_sizes, ["2 finger", "4 finger", "Chunky", "Mini"]),
            kitkat.allergens = COALESCE(kitkat.allergens, ["Milk", "Wheat", "Soy"]),
            kitkat.origin_country = COALESCE(kitkat.origin_country, "UK"),
            kitkat.fun_facts = COALESCE(kitkat.fun_facts, ["Most popular chocolate bar globally", "Available in 100+ countries"]),
            kitkat.last_enhanced = datetime()
        
        // Enhance Smarties (your existing product)  
        MERGE (smarties:Product {name: "Smarties"})
        SET smarties.target_audience = COALESCE(smarties.target_audience, "Children and families"),
            smarties.occasion = COALESCE(smarties.occasion, "Parties, baking, decorating"),
            smarties.no_artificial_colors = COALESCE(smarties.no_artificial_colors, true),
            smarties.allergens = COALESCE(smarties.allergens, ["Milk"]),
            smarties.baking_uses = COALESCE(smarties.baking_uses, ["Cake decoration", "Cookie mix-ins"]),
            smarties.last_enhanced = datetime()
        
        // Enhance Aero (your existing product)
        MERGE (aero:Product {name: "Aero"})  
        SET aero.unique_feature = COALESCE(aero.unique_feature, "Bubbly texture created by pressurized chocolate"),
            aero.target_audience = COALESCE(aero.target_audience, "Chocolate lovers seeking lighter texture"),
            aero.varieties = COALESCE(aero.varieties, ["Milk Chocolate", "Dark Chocolate", "Mint"]),
            aero.allergens = COALESCE(aero.allergens, ["Milk"]),
            aero.last_enhanced = datetime()
        
        // Enhance Coffee-mate (your existing product)
        MERGE (coffeemate:Product {name: "Coffee-mate"})
        SET coffeemate.varieties = COALESCE(coffeemate.varieties, ["Original", "French Vanilla", "Hazelnut"]),
            coffeemate.seasonal_flavors = COALESCE(coffeemate.seasonal_flavors, ["Pumpkin Spice", "Gingerbread"]),
            coffeemate.usage = COALESCE(coffeemate.usage, ["Coffee enhancement", "Baking ingredient"]),
            coffeemate.shelf_stable = COALESCE(coffeemate.shelf_stable, true),
            coffeemate.last_enhanced = datetime()
        
        // Enhance MILO (your existing product)
        MERGE (milo:Product {name: "MILO"})
        SET milo.inventor = COALESCE(milo.inventor, "Thomas Mayne"),
            milo.key_nutrients = COALESCE(milo.key_nutrients, ["Iron", "Calcium", "Vitamin C"]),
            milo.target_audience = COALESCE(milo.target_audience, "Active children and families"),
            milo.preparation = COALESCE(milo.preparation, ["Hot milk", "Cold milk", "Smoothies"]),
            milo.fun_facts = COALESCE(milo.fun_facts, ["Named after Greek athlete Milo of Croton"]),
            milo.last_enhanced = datetime()
        
        // Enhance Garden Gourmet Burger (your existing product)
        MERGE (garden:Product {name: "Garden Gourmet Burger"})
        SET garden.product_type = COALESCE(garden.product_type, "Plant-based meat alternative"),
            garden.target_audience = COALESCE(garden.target_audience, "Health-conscious consumers, vegetarians"),
            garden.cooking_instructions = COALESCE(garden.cooking_instructions, ["Pan fry", "Grill", "Oven bake"]),
            garden.key_benefits = COALESCE(garden.key_benefits, ["High protein", "No meat", "Sustainable"]),
            garden.last_enhanced = datetime()
        
        RETURN "Products safely enhanced" as status
        """
        
        session.run(enhancement_query)
        print("✅ Products safely enhanced without duplicates")
    
    def _safely_add_store_framework(self, session):
        """Add store information framework (only if not exists)"""
        print("🏪 Adding store framework (if not exists)...")
        
        # Split into separate queries to avoid variable redeclaration
        store_queries = [
            # Create individual store nodes
            """
            MERGE (walmart:Store {name: "Walmart"})
            ON CREATE SET walmart.type = "Supermarket Chain",
                         walmart.locations = "Nationwide Canada",
                         walmart.website = "walmart.ca",
                         walmart.created_at = datetime()
            """,
            
            """
            MERGE (loblaws:Store {name: "Loblaws"})
            ON CREATE SET loblaws.type = "Supermarket Chain",
                         loblaws.locations = "Ontario, Atlantic Canada", 
                         loblaws.website = "loblaws.ca",
                         loblaws.created_at = datetime()
            """,
            
            """
            MERGE (metro:Store {name: "Metro"})
            ON CREATE SET metro.type = "Supermarket Chain",
                         metro.locations = "Ontario, Quebec",
                         metro.website = "metro.ca", 
                         metro.created_at = datetime()
            """,
            
            """
            MERGE (sobeys:Store {name: "Sobeys"})
            ON CREATE SET sobeys.type = "Supermarket Chain",
                         sobeys.locations = "Nationwide Canada",
                         sobeys.website = "sobeys.com", 
                         sobeys.created_at = datetime()
            """,
            
            # Create availability relationships - KitKat to Walmart
            """
            MATCH (kitkat:Product {name: "KitKat"})
            MATCH (walmart:Store {name: "Walmart"})
            MERGE (kitkat)-[rel:AVAILABLE_AT]->(walmart)
            ON CREATE SET rel.section = "Chocolate aisle",
                         rel.typical_price_range = "$1.50-$8.99",
                         rel.created_at = datetime()
            """,
            
            # Create availability relationships - Smarties to Loblaws
            """
            MATCH (smarties:Product {name: "Smarties"})
            MATCH (loblaws:Store {name: "Loblaws"})
            MERGE (smarties)-[rel:AVAILABLE_AT]->(loblaws)
            ON CREATE SET rel.section = "Candy aisle",
                         rel.typical_price_range = "$2.99-$5.99",
                         rel.created_at = datetime()
            """,
            
            # Create availability relationships - Aero to Metro
            """
            MATCH (aero:Product {name: "Aero"})
            MATCH (metro:Store {name: "Metro"})
            MERGE (aero)-[rel:AVAILABLE_AT]->(metro)
            ON CREATE SET rel.section = "Chocolate aisle",
                         rel.typical_price_range = "$1.99-$6.99",
                         rel.created_at = datetime()
            """,
            
            # Create availability relationships - Coffee-mate to Sobeys
            """
            MATCH (coffeemate:Product {name: "Coffee-mate"})
            MATCH (sobeys:Store {name: "Sobeys"})
            MERGE (coffeemate)-[rel:AVAILABLE_AT]->(sobeys)
            ON CREATE SET rel.section = "Coffee aisle",
                         rel.typical_price_range = "$3.99-$7.99",
                         rel.created_at = datetime()
            """
        ]
        
        # Execute each query separately
        for i, query in enumerate(store_queries, 1):
            try:
                session.run(query)
                print(f"✅ Store query {i}/{len(store_queries)} completed")
            except Exception as e:
                print(f"⚠️ Store query {i} had issue: {e}")
                # Continue with other queries
        
        print("✅ Store framework safely added")
    
    def _safely_add_nutrition_data(self, session):
        """Add nutrition data only if it doesn't exist"""
        print("🥗 Adding nutrition data (if not exists)...")
        
        # Split nutrition queries to avoid variable conflicts
        nutrition_queries = [
            # KitKat nutrition
            """
            MATCH (kitkat:Product {name: "KitKat"})
            MERGE (kitkat_nutrition:Nutrition {product: "KitKat 4-finger bar"})
            ON CREATE SET kitkat_nutrition.serving_size = "41.5g",
                         kitkat_nutrition.calories = 210,
                         kitkat_nutrition.fat = "11g",
                         kitkat_nutrition.carbohydrates = "26g",
                         kitkat_nutrition.protein = "3g",
                         kitkat_nutrition.created_at = datetime()
            
            MERGE (kitkat)-[rel:HAS_NUTRITION]->(kitkat_nutrition)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # Smarties nutrition
            """
            MATCH (smarties:Product {name: "Smarties"})
            MERGE (smarties_nutrition:Nutrition {product: "Smarties"})
            ON CREATE SET smarties_nutrition.serving_size = "15 pieces (17g)",
                         smarties_nutrition.calories = 70,
                         smarties_nutrition.fat = "2.5g",
                         smarties_nutrition.carbohydrates = "12g",
                         smarties_nutrition.protein = "1g",
                         smarties_nutrition.created_at = datetime()
            
            MERGE (smarties)-[rel:HAS_NUTRITION]->(smarties_nutrition)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # MILO nutrition
            """
            MATCH (milo:Product {name: "MILO"})
            MERGE (milo_nutrition:Nutrition {product: "MILO powder"})
            ON CREATE SET milo_nutrition.serving_size = "20g (3 tsp)",
                         milo_nutrition.calories = 80,
                         milo_nutrition.protein = "1.5g",
                         milo_nutrition.iron = "3.6mg (45% DV)",
                         milo_nutrition.calcium = "90mg",
                         milo_nutrition.created_at = datetime()
            
            MERGE (milo)-[rel:HAS_NUTRITION]->(milo_nutrition)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # Aero nutrition
            """
            MATCH (aero:Product {name: "Aero"})
            MERGE (aero_nutrition:Nutrition {product: "Aero bar"})
            ON CREATE SET aero_nutrition.serving_size = "42g",
                         aero_nutrition.calories = 200,
                         aero_nutrition.fat = "10g",
                         aero_nutrition.carbohydrates = "25g",
                         aero_nutrition.protein = "3g",
                         aero_nutrition.created_at = datetime()
            
            MERGE (aero)-[rel:HAS_NUTRITION]->(aero_nutrition)
            ON CREATE SET rel.created_at = datetime()
            """
        ]
        
        # Execute each nutrition query separately
        for i, query in enumerate(nutrition_queries, 1):
            try:
                session.run(query)
                print(f"✅ Nutrition query {i}/{len(nutrition_queries)} completed")
            except Exception as e:
                print(f"⚠️ Nutrition query {i} had issue: {e}")
                # Continue with other queries
        
        print("✅ Nutrition data safely added")
    
    def _safely_enhance_sustainability(self, session):
        """Enhance existing sustainability topics"""
        print("🌱 Enhancing sustainability information...")
        
        # Split sustainability queries to avoid variable conflicts
        sustainability_queries = [
            # Enhance existing Cocoa Sustainability topic
            """
            MERGE (cocoa:Topic {name: "Cocoa Sustainability"})
            SET cocoa.investment = COALESCE(cocoa.investment, "$1.3 billion by 2030"),
                cocoa.farmers_reached = COALESCE(cocoa.farmers_reached, "300,000+ farmers"),
                cocoa.countries = COALESCE(cocoa.countries, ["Ivory Coast", "Ghana", "Ecuador"]),
                cocoa.achievements = COALESCE(cocoa.achievements, [
                    "175,000 farmers trained",
                    "86,000 cocoa seedlings distributed"
                ]),
                cocoa.last_enhanced = datetime()
            """,
            
            # Add Water Stewardship topic
            """
            MERGE (water:Topic {name: "Water Stewardship"})
            ON CREATE SET water.description = "Protecting water resources for current and future generations",
                         water.goal = "Achieve water efficiency across all operations",
                         water.achievements = ["40% reduction in water usage per ton"],
                         water.created_at = datetime()
            """,
            
            # Add Climate Action topic
            """
            MERGE (climate:Topic {name: "Climate Action"})
            ON CREATE SET climate.description = "Nestlé's commitment to net zero greenhouse gas emissions",
                         climate.target_year = 2050,
                         climate.interim_target = "50% reduction by 2030",
                         climate.created_at = datetime()
            """,
            
            # Add Sustainable Packaging topic
            """
            MERGE (sustain_packaging:Topic {name: "Sustainable Packaging"})
            ON CREATE SET sustain_packaging.description = "Making 95% of packaging recyclable by 2025",
                         sustain_packaging.current_progress = "77% recyclable packaging",
                         sustain_packaging.created_at = datetime()
            """
        ]
        
        # Connection queries
        connection_queries = [
            # Connect KitKat to Sustainable Packaging
            """
            MATCH (kitkat:Product {name: "KitKat"})
            MATCH (sustain_packaging:Topic {name: "Sustainable Packaging"})
            MERGE (kitkat)-[rel:USES]->(sustain_packaging)
            ON CREATE SET rel.type = "Recyclable wrapper",
                         rel.created_at = datetime()
            """,
            
            # Connect Nestlé Canada to Water Stewardship
            """
            MATCH (nestle_canada:Company {name: "Nestlé Canada"})
            MATCH (water:Topic {name: "Water Stewardship"})
            MERGE (nestle_canada)-[rel:PRACTICES]->(water)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # Connect Nestlé Canada to Climate Action
            """
            MATCH (nestle_canada:Company {name: "Nestlé Canada"})
            MATCH (climate:Topic {name: "Climate Action"})
            MERGE (nestle_canada)-[rel:COMMITTED_TO]->(climate)
            ON CREATE SET rel.created_at = datetime()
            """
        ]
        
        # Execute sustainability enhancement queries
        for i, query in enumerate(sustainability_queries, 1):
            try:
                session.run(query)
                print(f"✅ Sustainability query {i}/{len(sustainability_queries)} completed")
            except Exception as e:
                print(f"⚠️ Sustainability query {i} had issue: {e}")
        
        # Execute connection queries
        for i, query in enumerate(connection_queries, 1):
            try:
                session.run(query)
                print(f"✅ Sustainability connection {i}/{len(connection_queries)} completed")
            except Exception as e:
                print(f"⚠️ Sustainability connection {i} had issue: {e}")
        
        print("✅ Sustainability information safely enhanced")
    
    def _safely_add_faq_framework(self, session):
        """Add FAQ framework without duplicates"""
        print("❓ Adding FAQ framework...")
        
        # Split FAQ queries to avoid variable conflicts
        faq_queries = [
            # FAQ 1 - KitKat availability
            """
            MERGE (faq1:FAQ {question: "Where can I buy KitKat?"})
            ON CREATE SET faq1.answer = "KitKat is available at major retailers across Canada including Walmart, Loblaws, Metro, and convenience stores.",
                         faq1.category = "Availability",
                         faq1.products = ["KitKat"],
                         faq1.created_at = datetime()
            """,
            
            # FAQ 2 - Cocoa sustainability
            """
            MERGE (faq2:FAQ {question: "Is Nestlé cocoa sustainable?"})
            ON CREATE SET faq2.answer = "Yes, Nestlé is committed to sourcing 100% sustainable cocoa by 2025 through the Nestlé Cocoa Plan.",
                         faq2.category = "Sustainability",
                         faq2.products = ["KitKat", "Smarties", "Aero"],
                         faq2.created_at = datetime()
            """,
            
            # FAQ 3 - MILO nutrition
            """
            MERGE (faq3:FAQ {question: "What nutrients are in MILO?"})
            ON CREATE SET faq3.answer = "MILO contains Iron (45% DV), Calcium, Vitamin C, Vitamin D, and B-vitamins for active lifestyles.",
                         faq3.category = "Nutrition",
                         faq3.products = ["MILO"],
                         faq3.created_at = datetime()
            """,
            
            # FAQ 4 - What's new
            """
            MERGE (faq4:FAQ {question: "What's new at Nestlé?"})
            ON CREATE SET faq4.answer = "Nestlé continuously innovates with new products, sustainable packaging, and community initiatives. Check our latest news for updates.",
                         faq4.category = "Company Updates",
                         faq4.created_at = datetime()
            """,
            
            # FAQ 5 - Smarties for children
            """
            MERGE (faq5:FAQ {question: "Are Smarties suitable for children?"})
            ON CREATE SET faq5.answer = "Yes, Smarties are made with no artificial colors and are enjoyed by children and families as part of a balanced diet.",
                         faq5.category = "Product Information",
                         faq5.products = ["Smarties"],
                         faq5.created_at = datetime()
            """
        ]
        
        # Connection queries
        connection_queries = [
            # Connect FAQ1 to KitKat
            """
            MATCH (kitkat:Product {name: "KitKat"})
            MATCH (faq1:FAQ {question: "Where can I buy KitKat?"})
            MERGE (faq1)-[rel:ANSWERS_ABOUT]->(kitkat)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # Connect FAQ3 to MILO
            """
            MATCH (milo:Product {name: "MILO"})
            MATCH (faq3:FAQ {question: "What nutrients are in MILO?"})
            MERGE (faq3)-[rel:ANSWERS_ABOUT]->(milo)
            ON CREATE SET rel.created_at = datetime()
            """,
            
            # Connect FAQ5 to Smarties
            """
            MATCH (smarties:Product {name: "Smarties"})
            MATCH (faq5:FAQ {question: "Are Smarties suitable for children?"})
            MERGE (faq5)-[rel:ANSWERS_ABOUT]->(smarties)
            ON CREATE SET rel.created_at = datetime()
            """
        ]
        
        # Execute FAQ creation queries
        for i, query in enumerate(faq_queries, 1):
            try:
                session.run(query)
                print(f"✅ FAQ {i}/{len(faq_queries)} created")
            except Exception as e:
                print(f"⚠️ FAQ {i} creation issue: {e}")
        
        # Execute connection queries
        for i, query in enumerate(connection_queries, 1):
            try:
                session.run(query)
                print(f"✅ FAQ connection {i}/{len(connection_queries)} created")
            except Exception as e:
                print(f"⚠️ FAQ connection {i} issue: {e}")
        
        print("✅ FAQ framework safely added")

# Usage
safe_enhancer = SafeDataEnhancer()