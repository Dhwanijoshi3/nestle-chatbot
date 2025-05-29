# quick_test.py - Test your Neo4j data directly

from backend.neo4j_connection import neo4j_conn

def test_ceo_query():
    """Test CEO query directly"""
    print("🔍 Testing CEO query...")
    
    try:
        with neo4j_conn.get_session() as session:
            # Test CEO query
            query = """
            MATCH (p:Person)
            WHERE toLower(p.name) CONTAINS 'schneider' 
               OR toLower(p.role) CONTAINS 'ceo'
            RETURN p.name as name, p.role as role
            """
            
            result = session.run(query)
            records = list(result)
            
            print(f"Found {len(records)} CEO records:")
            for record in records:
                print(f"  • {record['name']}: {record.get('role', 'N/A')}")
            
            if records:
                return f"**{records[0]['name']}** is the CEO of Nestlé globally."
            else:
                return "CEO information not found in database."
                
    except Exception as e:
        return f"Error: {e}"

def test_product_query():
    """Test product query"""
    print("\n🔍 Testing product query...")
    
    try:
        with neo4j_conn.get_session() as session:
            query = """
            MATCH (p:Product {name: 'KitKat'})
            RETURN p.name as name, p.description as description, p.tagline as tagline
            """
            
            result = session.run(query)
            record = result.single()
            
            if record:
                print(f"  • Product: {record['name']}")
                print(f"  • Description: {record.get('description', 'N/A')}")
                print(f"  • Tagline: {record.get('tagline', 'N/A')}")
                return f"**{record['name']}** - {record.get('tagline', 'Chocolate wafer bar')}"
            else:
                return "KitKat product not found in database."
                
    except Exception as e:
        return f"Error: {e}"

def test_store_query():
    """Test store availability"""
    print("\n🔍 Testing store query...")
    
    try:
        with neo4j_conn.get_session() as session:
            query = """
            MATCH (s:Store)
            RETURN s.name as name, s.type as type, s.locations as locations
            LIMIT 5
            """
            
            result = session.run(query)
            records = list(result)
            
            print(f"Found {len(records)} stores:")
            for record in records:
                print(f"  • {record['name']}: {record.get('type', 'Store')} - {record.get('locations', 'Various locations')}")
            
            if records:
                stores = [f"**{r['name']}** - {r.get('locations', 'Various locations')}" for r in records]
                return f"Available at: {', '.join(stores[:3])}"
            else:
                return "Store information not found in database."
                
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("🧪 Testing Neo4j Queries Directly")
    print("="*50)
    
    if neo4j_conn.connect():
        print("✅ Neo4j connection successful")
        
        # Test CEO query
        ceo_result = test_ceo_query()
        print(f"CEO Query Result: {ceo_result}")
        
        # Test product query  
        product_result = test_product_query()
        print(f"Product Query Result: {product_result}")
        
        # Test store query
        store_result = test_store_query()
        print(f"Store Query Result: {store_result}")
        
        print("\n✅ All tests completed!")
        print("\nIf these work, your chatbot should work perfectly!")
        
    else:
        print("❌ Neo4j connection failed")