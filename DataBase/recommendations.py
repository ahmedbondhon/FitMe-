# database/recommendations.py - CLEAN VERSION
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

def get_recommendations(db: Session, profile_id: int):
    """
    Get clothing recommendations based on user profile
    Returns real data from database or empty list if no data found
    """
    print(f"🔍 Starting get_recommendations for profile_id: {profile_id}")
    
    try:
        # Get all table names in database
        inspector = inspect(db.bind)
        table_names = inspector.get_table_names()
        print(f"📊 Available tables: {table_names}")
        
        # Check if required tables exist
        if 'user_profiles' not in table_names:
            print("❌ user_profiles table does not exist")
            return []
        
        # Get user profile
        profile_query = text("""
            SELECT gender_id, life_stage_id, occasion_id, price_range_id, season_id, 
                   body_type_id, skin_tone_id, unisex_preference
            FROM user_profiles WHERE id = :pid
        """)
        profile = db.execute(profile_query, {"pid": profile_id}).fetchone()
        
        if not profile:
            print(f"❌ No profile found with ID: {profile_id}")
            return []
        
        print(f"✅ User profile found - Gender: {profile[0]}, Unisex: {profile[7]}")
        
        # Find available clothing tables
        clothing_tables = []
        for table_name in ['men_clothes', 'women_clothes', 'unisex_clothes']:
            if table_name in table_names:
                clothing_tables.append(table_name)
                print(f"✅ Found clothing table: {table_name}")
        
        if not clothing_tables:
            print("❌ No clothing tables found")
            return []
        
        # Determine target table based on gender and preferences
        gender_id = profile[0]
        unisex_preference = profile[7]
        
        if unisex_preference:
            target_table = 'unisex_clothes'
        elif gender_id == 1:  # Male
            target_table = 'men_clothes'
        elif gender_id == 2:  # Female
            target_table = 'women_clothes'
        else:  # Default to unisex
            target_table = 'unisex_clothes'
        
        # Use first available table if target doesn't exist
        if target_table not in clothing_tables:
            target_table = clothing_tables[0]
        
        print(f" Querying table: {target_table}")
        
        # Check if table has data
        count_query = text(f"SELECT COUNT(*) FROM {target_table}")
        item_count = db.execute(count_query).fetchone()[0]
        
        if item_count == 0:
            print(f" {target_table} is empty")
            return []
        
        print(f" Found {item_count} items in {target_table}")
        
        # Get recommendations from database
        query = text(f"""
            SELECT cloth_id, name, color, size, price, image_url, category_id 
            FROM {target_table} 
            LIMIT 6
        """)
        items = db.execute(query).fetchall()
        
        # Process results
        recommendations = []
        category_map = {
            1: "Shirts",
            2: "Pants", 
            3: "Shoes",
            4: "Socks",
            5: "Hats"
        }
        
        for item in items:
            recommendations.append({
                "id": item[0],
                "title": item[1],
                "color": item[2],
                "size": item[3],
                "price": float(item[4]) if item[4] else 0.0,
                "category": category_map.get(item[6], "Clothing"),
                "image_url": item[5] or f"https://via.placeholder.com/300?text={item[1].replace(' ', '+')}"
            })
        
        print(f" Successfully generated {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        print(f" Error in get_recommendations: {e}")
        return []