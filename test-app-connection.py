# test-app-connection.py
"""
Test your FastAPI application's connection to Azure MySQL
"""
import os
import sys

# Set environment variables for testing
os.environ['DB_HOST'] = 'infinityai-mysql-west-eur.mysql.database.azure.com'
os.environ['DB_USER'] = 'infinityai_admin'
os.environ['DB_PASSWORD'] = 'InfinityAI@MySQL2024!SecurePass#123'
os.environ['DB_NAME'] = 'infinityai'
os.environ['DB_SSL_VERIFY'] = 'false'
os.environ['TESTING'] = '0'  # Force MySQL (not SQLite)

print("🧪 Testing FastAPI App with Azure MySQL")
print("=" * 50)

try:
    # Import your database manager
    sys.path.append(os.getcwd())
    from shared.utils.database import db
    
    # Test database connection
    print("🔗 Testing database connection...")
    if db.test_connection():
        print("✅ Database connection successful!")
        
        # Test queries
        print("\n📊 Testing database queries...")
        
        # Test user query
        users = db.execute_query("SELECT username, email FROM users LIMIT 3")
        print(f"✅ Found {len(users)} users:")
        for user in users:
            print(f"   - {user['username']} ({user['email']})")
        
        # Test table count
        tables = db.execute_query("""
            SELECT TABLE_NAME, TABLE_ROWS 
            FROM information_schema.tables 
            WHERE table_schema = 'infinityai'
        """)
        
        print(f"\n📋 Database tables ({len(tables)} total):")
        for table in tables:
            print(f"   - {table['TABLE_NAME']}: {table['TABLE_ROWS']} rows")
        
        print("\n🎉 FastAPI app can successfully connect to Azure MySQL!")
        
        # Test health endpoint simulation
        print("\n🏥 Simulating health check...")
        health_status = {
            "status": "healthy",
            "database": "connected" if db.test_connection() else "disconnected",
            "tables": len(tables),
            "service": "infinityai-backend-app"
        }
        print(f"Health check result: {health_status}")
        
    else:
        print("❌ Database connection failed!")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎯 Next Steps:")
print("1. ✅ Azure MySQL database is working with your app")
print("2. 🔄 Update GitHub DATABASE_URL secret (already done)")  
print("3. 🚀 Deploy to Azure Container App")
print("4. 🧪 Run comprehensive API tests")