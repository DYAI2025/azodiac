---
description: Query MongoDB on remote systems via SSH
allowed-tools: [Bash, Read, Write]
---

## Context
You are querying a MongoDB database running on a remote system via SSH. This avoids needing to install MongoDB client locally and works through SSH tunnels.

## Your Task

Execute MongoDB queries on a remote system and return formatted results without requiring local MongoDB installation.

### Steps

1. **Gather Connection Information**
   Ask user for:
   - Remote host (IP or hostname)
   - SSH username
   - MongoDB host (usually `localhost` from remote perspective)
   - MongoDB port (default: 27017)
   - Database name
   - MongoDB credentials (if auth enabled)

2. **Test SSH Connection**
   ```bash
   ssh USER@REMOTE_HOST "echo 'SSH connection working'"
   ```

3. **Check MongoDB Availability**
   ```bash
   ssh USER@REMOTE_HOST "netstat -tulpn 2>/dev/null | grep 27017 || ss -tulpn 2>/dev/null | grep 27017"
   ```

4. **Determine Query Approach**

   Ask user what they want to do:
   - List all databases
   - List collections in a database
   - Count documents in a collection
   - Query specific data
   - Aggregate/complex query

5. **Execute Query via Python**

   Create a Python script on the remote system:

   ```bash
   ssh USER@REMOTE_HOST 'cat > /tmp/mongo_query.py << '\''EOF'\''
   from pymongo import MongoClient
   import json

   # Connection string
   client = MongoClient("mongodb://USERNAME:PASSWORD@localhost:27017/DATABASE?authSource=admin")
   db = client.DATABASE_NAME

   # Your query here
   results = db.COLLECTION.find({}).limit(10)

   for doc in results:
       print(json.dumps(doc, indent=2, default=str))
   EOF
   source ~/.venv/bin/activate && python3 /tmp/mongo_query.py'
   ```

6. **Format Results**

   Present results in user-friendly format:
   - **JSON** - For detailed data
   - **Table** - For summary views
   - **Count** - For statistics
   - **List** - For simple queries

### Common Query Templates

**List Databases:**
```python
from pymongo import MongoClient
client = MongoClient("mongodb://admin:password@localhost:27017/?authSource=admin")
print("Databases:", client.list_database_names())
```

**List Collections:**
```python
from pymongo import MongoClient
client = MongoClient("mongodb://admin:password@localhost:27017/dbname?authSource=admin")
db = client.dbname
print("Collections:", db.list_collection_names())
```

**Count Documents:**
```python
from pymongo import MongoClient
client = MongoClient("mongodb://admin:password@localhost:27017/dbname?authSource=admin")
db = client.dbname
for collection in db.list_collection_names():
    count = db[collection].count_documents({})
    print(f"{collection}: {count} documents")
```

**Query Collection:**
```python
from pymongo import MongoClient
import json

client = MongoClient("mongodb://admin:password@localhost:27017/dbname?authSource=admin")
db = client.dbname

# Find all
results = db.collection_name.find({})

# Find with filter
results = db.collection_name.find({"user_id": "ben"})

# Find with projection
results = db.collection_name.find({}, {"_id": 0, "name": 1, "email": 1})

for doc in results:
    print(json.dumps(doc, indent=2, default=str))
```

**Aggregate Query:**
```python
from pymongo import MongoClient

client = MongoClient("mongodb://admin:password@localhost:27017/dbname?authSource=admin")
db = client.dbname

pipeline = [
    {"$match": {"status": "active"}},
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]

results = db.collection_name.aggregate(pipeline)
for doc in results:
    print(doc)
```

### Guardrails
- **Never log passwords** in output or error messages
- **Use authSource=admin** for admin user authentication
- **Escape quotes** properly in heredoc (use `'\''` for single quotes in bash heredoc)
- **Clean up temp files** after query: `ssh USER@HOST "rm /tmp/mongo_query.py"`
- **Limit large queries** with `.limit()` to avoid overwhelming output
- **Handle ObjectId** with `default=str` in json.dumps

### Connection String Format

```
mongodb://[username:password@]host[:port]/[database][?options]
```

**Examples:**
```
# No auth
mongodb://localhost:27017/mydb

# With auth
mongodb://admin:password@localhost:27017/mydb?authSource=admin

# With options
mongodb://admin:password@localhost:27017/mydb?authSource=admin&socketTimeoutMS=15000
```

### Error Handling

**"pymongo not installed":**
```bash
ssh USER@HOST "pip install pymongo || pip3 install pymongo"
```

**"Authentication failed":**
- Check username/password
- Verify authSource (usually "admin" for admin users)
- Check if user has access to the database

**"Connection refused":**
- Verify MongoDB is running: `ps aux | grep mongod`
- Check port: `netstat -tulpn | grep 27017`
- Check if MongoDB binds to localhost only

**"Module not found":**
- Activate correct virtual environment
- Or use full path to Python with pymongo installed

### Alternative: mongosh (if available)

If mongosh is installed on remote system:
```bash
ssh USER@HOST "mongosh --quiet mongodb://admin:password@localhost:27017/dbname --authenticationDatabase admin --eval 'db.collection.find().limit(5)'"
```

---
*Generated by /reflect-skills from EvermemOS MongoDB query patterns*
