# backend/neo4j_data_initializer.py - Initialize Neo4j Aura with Nestlé Data

from .neo4j_connection import neo4j_conn

class Neo4jDataInitializer:
    """Initialize Neo4j Aura with comprehensive Nestlé data"""
    
    def __init__(self):
        pass
    
    def initialize_data(self):
        """Create comprehensive Nestlé knowledge graph (preserving existing data)"""
        print("🏗️ Checking and enhancing Neo4j with Nestlé data...")
        
        try:
            with neo4j_conn.get_session() as session:
                # Check existing data
                result = session.run("MATCH (n) RETURN count(n) as count")
                existing_count = result.single()['count']
                print(f"📊 Found {existing_count} existing nodes")
                
                if existing_count > 0:
                    print("✅ Preserving existing data and adding missing core entities...")
                    self._enhance_existing_data(session)
                else:
                    print("📊 No existing data found, creating complete dataset...")
                    self._create_core_data(session)
                
                # Verify final state
                result = session.run("MATCH (n) RETURN labels(n)[0] as type, count(*) as count ORDER BY count DESC")
                print("✅ Data initialization/enhancement completed!")
                print("📊 Final node counts:")
                for record in result:
                    print(f"   {record['type']}: {record['count']}")
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to initialize data: {e}")
            return False
    
    def _enhance_existing_data(self, session):
        """Add missing core entities without overwriting existing data"""
        
        # Only add missing essential entities using MERGE (won't duplicate)
        enhancement_query = """
        // Ensure core companies exist
        MERGE (nestleGlobal:Company {name: "Nestlé"})
        ON CREATE SET nestleGlobal.description = "World's largest food and beverage company",
                     nestleGlobal.founded = 1866,
                     nestleGlobal.headquarters = "Vevey, Switzerland"
        
        MERGE (nestleCanada:Company {name: "Nestlé Canada"})
        ON CREATE SET nestleCanada.description = "Leading food and beverage company in Canada",
                     nestleCanada.founded = 1918,
                     nestleCanada.headquarters = "Toronto, Canada"
        
        // Ensure core categories exist
        MERGE (chocolate:Category {name: "Chocolate & Confectionery"})
        ON CREATE SET chocolate.description = "Premium chocolate bars and confectionery treats"
        
        MERGE (beverages:Category {name: "Coffee & Beverages"})
        ON CREATE SET beverages.description = "Coffee, creamers, and beverage products"
        
        // Ensure sustainability topics exist
        MERGE (cocoaPlan:Topic {name: "Nestlé Cocoa Plan"})
        ON CREATE SET cocoaPlan.description = "Program to improve lives of cocoa farmers and quality of cocoa",
                     cocoaPlan.launched = 2009
        
        MERGE (sustainability:Topic {name: "Sustainability"})
        ON CREATE SET sustainability.description = "Environmental stewardship and social responsibility commitment"
        
        // Ensure core leadership exists
        MERGE (markSchneider:Person {name: "Mark Schneider"})
        ON CREATE SET markSchneider.role = "CEO",
                     markSchneider.company = "Nestlé Global"
        
        // Create essential relationships (only if they don't exist)
        MERGE (nestleCanada)-[:SUBSIDIARY_OF]->(nestleGlobal)
        MERGE (markSchneider)-[:CEO_OF]->(nestleGlobal)
        MERGE (nestleCanada)-[:COMMITTED_TO]->(sustainability)
        
        RETURN "Enhancement completed" as status
        """
        
        session.run(enhancement_query)
        print("✅ Core entities enhanced successfully")
    
    def _create_core_data(self, session):
        """Create the core Nestlé knowledge graph (for empty databases)"""
        
        data_query = """
        // Core Company
        MERGE (nestleCanada:Company {name: "Nestlé Canada"})
        SET nestleCanada.description = "Leading food and beverage company in Canada with over 100 years of history",
            nestleCanada.founded = 1918,
            nestleCanada.headquarters = "Toronto, Canada",
            nestleCanada.mission = "Good Food, Good Life",
            nestleCanada.employees = "3000+"

        MERGE (nestleGlobal:Company {name: "Nestlé"})
        SET nestleGlobal.description = "World's largest food and beverage company",
            nestleGlobal.founded = 1866,
            nestleGlobal.headquarters = "Vevey, Switzerland",
            nestleGlobal.ceo = "Mark Schneider"

        // Product Categories  
        MERGE (chocolate:Category {name: "Chocolate & Confectionery"})
        SET chocolate.description = "Premium chocolate bars, confectionery, and seasonal treats"

        MERGE (beverages:Category {name: "Coffee & Beverages"})
        SET beverages.description = "Coffee, creamers, and hot beverage products"

        MERGE (dairy:Category {name: "Dairy & Nutrition"})
        SET dairy.description = "Milk products, infant nutrition, and health-focused foods"

        // Core Products (only add if they don't exist)
        MERGE (kitkat:Product {name: "KitKat"})
        ON CREATE SET kitkat.description = "Iconic chocolate wafer bar with crispy wafer fingers covered in milk chocolate",
                     kitkat.launched = 1935,
                     kitkat.tagline = "Have a break, have a KitKat"

        MERGE (smarties:Product {name: "Smarties"})
        ON CREATE SET smarties.description = "Colorful chocolate candies with a crispy sugar shell and creamy milk chocolate center",
                     smarties.launched = 1937,
                     smarties.colors = ["Red", "Orange", "Yellow", "Green", "Blue", "Mauve", "Pink", "Brown"]

        MERGE (aero:Product {name: "Aero"})
        ON CREATE SET aero.description = "Light, bubbly chocolate bar with unique aerated texture",
                     aero.launched = 1935,
                     aero.texture = "Aerated bubbles"

        MERGE (coffeemate:Product {name: "Coffee-mate"})
        ON CREATE SET coffeemate.description = "Premium coffee creamer that transforms your coffee experience",
                     coffeemate.varieties = ["Original", "French Vanilla", "Hazelnut", "Caramel"]

        // Sustainability Topics
        MERGE (cocoaPlan:Topic {name: "Nestlé Cocoa Plan"})
        SET cocoaPlan.description = "Comprehensive program to improve lives of cocoa farmers and quality of cocoa",
            cocoaPlan.launched = 2009,
            cocoaPlan.goals = ["Better farming", "Better lives", "Better cocoa"]

        MERGE (sustainability:Topic {name: "Sustainability"})
        SET sustainability.description = "Commitment to environmental stewardship and social responsibility",
            sustainability.focus_areas = ["Climate change", "Water stewardship", "Sustainable packaging"]

        // Leadership
        MERGE (markSchneider:Person {name: "Mark Schneider"})
        SET markSchneider.role = "CEO",
            markSchneider.company = "Nestlé Global"

        // Create key relationships
        MERGE (nestleCanada)-[:SUBSIDIARY_OF]->(nestleGlobal)
        MERGE (markSchneider)-[:CEO_OF]->(nestleGlobal)
        
        // Product relationships
        MERGE (kitkat)-[:BELONGS_TO]->(chocolate)
        MERGE (smarties)-[:BELONGS_TO]->(chocolate)
        MERGE (aero)-[:BELONGS_TO]->(chocolate)
        MERGE (coffeemate)-[:BELONGS_TO]->(beverages)
        
        MERGE (kitkat)-[:PRODUCED_BY]->(nestleCanada)
        MERGE (smarties)-[:PRODUCED_BY]->(nestleCanada)
        MERGE (aero)-[:PRODUCED_BY]->(nestleCanada)
        MERGE (coffeemate)-[:PRODUCED_BY]->(nestleCanada)
        
        // Sustainability relationships
        MERGE (kitkat)-[:SUPPORTS]->(cocoaPlan)
        MERGE (smarties)-[:SUPPORTS]->(cocoaPlan)
        MERGE (aero)-[:SUPPORTS]->(cocoaPlan)
        MERGE (nestleCanada)-[:COMMITTED_TO]->(sustainability)

        RETURN "Data creation completed" as status
        """
        
        session.run(data_query)
        print("✅ Core data created successfully")

data_initializer = Neo4jDataInitializer()