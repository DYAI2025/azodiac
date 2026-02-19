---
description: Connect services across machines for remote data/API access
allowed-tools: [Bash, Read, Write, Edit, AskUserQuestion]
---

## Context
When a service on Machine A needs to access data or services on Machine B (database, API, memory store, etc.), this skill provides a systematic integration workflow with primary and fallback methods.

## Your Task

Establish reliable cross-machine service integration with connectivity testing, dependency setup, and fallback configuration.

### Steps

1. **Understand the Integration Requirements**

   Ask user:
   - **Source:** Which service needs access? (e.g., OpenClaw on VPS)
   - **Target:** What does it need to access? (e.g., MongoDB on Linux PC)
   - **Purpose:** What will it do with the data? (query memories, write logs, etc.)
   - **Machines:** What are the hostnames/IPs?
   - **Network:** Tailscale, direct IP, VPN, localhost tunnel?

2. **Test Network Connectivity**

   Verify machines can reach each other:
   ```bash
   # From source machine
   ssh USER@SOURCE_HOST "ping -c 3 TARGET_IP"
   ```

   **Common issues:**
   - Tailscale SSH authentication required → Guide user to auth URL
   - VPS offline/unreachable → Check hosting panel, wait for restart
   - Firewall blocking → Check port accessibility
   - Network timeout → Verify IPs, check Tailscale status

3. **Identify Primary Integration Method**

   Choose based on service type:

   **Database (MongoDB, PostgreSQL, Redis):**
   - Primary: Direct connection via client library
   - Example: `mongodb://user:pass@TARGET_IP:27017/db`

   **HTTP API (REST, GraphQL):**
   - Primary: HTTP client (curl, fetch, requests)
   - Example: `http://TARGET_IP:8000/api/endpoint`

   **File-based (NFS, Samba, SSH):**
   - Primary: Mount or SSH file transfer
   - Example: `ssh USER@TARGET_IP "cat /path/to/file"`

4. **Install Required Dependencies**

   On source machine:
   ```bash
   # Check if dependencies exist
   ssh USER@SOURCE_HOST "python3 -c 'import pymongo' 2>&1"

   # Install if needed
   ssh USER@SOURCE_HOST "pip3 install pymongo"

   # If system Python blocked, use venv:
   ssh USER@SOURCE_HOST "~/.venv/bin/pip install pymongo"
   ```

   **Guardrails:**
   - Check for existing virtual environments before system install
   - Use `--user` flag if system packages are restricted
   - Test import after installation to verify

5. **Create Integration Script**

   Write a script on source machine to query/access target:

   **Template (Python + MongoDB example):**
   ```python
   #!/path/to/venv/bin/python3
   """
   Service Integration: [SOURCE] → [TARGET]
   """

   from pymongo import MongoClient
   from datetime import datetime

   # Configuration
   PRIMARY_URI = 'mongodb://user:pass@TARGET_IP:27017/'
   FALLBACK_API = 'http://TARGET_IP:8000/api/'
   DB_NAME = 'database_name'

   def connect_primary():
       """Primary method: Direct database connection"""
       try:
           client = MongoClient(PRIMARY_URI, serverSelectionTimeoutMS=5000)
           return client[DB_NAME]
       except Exception as e:
           print(f"Primary connection failed: {e}")
           return None

   def connect_fallback():
       """Fallback method: HTTP API"""
       import requests
       try:
           response = requests.get(f"{FALLBACK_API}health", timeout=5)
           if response.ok:
               return FALLBACK_API
       except Exception as e:
           print(f"Fallback connection failed: {e}")
       return None

   def query_data(db):
       """Execute query"""
       # Your query logic here
       results = list(db['collection'].find().limit(10))
       return results

   if __name__ == '__main__':
       # Try primary
       db = connect_primary()
       if db:
           print("✓ Connected via primary method")
           data = query_data(db)
           print(f"Retrieved {len(data)} records")
       else:
           # Fallback to API
           api = connect_fallback()
           if api:
               print("✓ Connected via fallback API")
               # Use API instead
           else:
               print("✗ All connection methods failed")
   ```

   Save script on source machine with appropriate permissions:
   ```bash
   ssh USER@SOURCE_HOST "cat > ~/integration_script.py << 'EOF'
   [script content]
   EOF
   chmod +x ~/integration_script.py"
   ```

6. **Test Primary Connection**

   ```bash
   ssh USER@SOURCE_HOST "~/integration_script.py"
   ```

   Verify:
   - ✓ Connection established
   - ✓ Authentication successful
   - ✓ Data retrieval works
   - ✓ Latency acceptable

   **If fails:**
   - Check credentials
   - Verify target service is running
   - Test manually: `ssh USER@TARGET_HOST "systemctl status service"`

7. **Set Up Fallback Method**

   If primary is direct connection, fallback should be API-based:

   **Start API on target machine:**
   ```bash
   # Example: Start FastAPI service
   ssh USER@TARGET_HOST "cd /path/to/api && uvicorn app:app --host 0.0.0.0 --port 8000"
   ```

   **Test fallback:**
   ```bash
   ssh USER@SOURCE_HOST "curl -s http://TARGET_IP:8000/health"
   ```

   **Configure fallback in integration script:**
   - Add try/except around primary method
   - Fall back to HTTP API if primary fails
   - Log which method was used

8. **Configure Service to Use Integration**

   Update source service configuration:

   **For OpenClaw/config-based services:**
   ```bash
   # Add to config file
   ssh USER@SOURCE_HOST "cat >> ~/.service/config.json << 'EOF'
   {
     \"memory\": {
       \"type\": \"remote\",
       \"primary\": \"mongodb://user:pass@TARGET_IP:27017/db\",
       \"fallback\": \"http://TARGET_IP:8000/api/memory\"
     }
   }
   EOF"
   ```

   **For cron-based queries:**
   ```bash
   # Add cron job to sync data periodically
   ssh USER@SOURCE_HOST "(crontab -l; echo '*/15 * * * * ~/integration_script.py >> ~/integration.log 2>&1') | crontab -"
   ```

9. **Test End-to-End**

   Verify complete workflow:
   ```bash
   # Trigger service action that requires remote data
   ssh USER@SOURCE_HOST "service_command_that_needs_remote_data"

   # Check logs for success
   ssh USER@SOURCE_HOST "tail -20 ~/integration.log"
   ```

   **Verify:**
   - Service can query remote data
   - Results are correct and complete
   - Performance is acceptable
   - Fallback works if primary fails

10. **Document the Integration**

    Create summary for future reference:
    ```
    ═══ CROSS-MACHINE INTEGRATION ═══

    Source: [Service Name] on [Machine A]
    Target: [Data/Service] on [Machine B]

    PRIMARY METHOD:
    - Type: Direct database connection / HTTP API / File access
    - Connection: [connection string/URL]
    - Script: [path to integration script]
    - Status: ✓ Working

    FALLBACK METHOD:
    - Type: HTTP API / Alternative connection
    - Endpoint: [API URL]
    - Status: ✓ Configured

    TESTING:
    - Network latency: [X]ms
    - Query performance: [Y] records in [Z]s
    - Verified: [date]

    MAINTENANCE:
    - Monitor: Check ~/integration.log
    - Update credentials: [where to update]
    - Restart if needed: [restart command]
    ```

### Common Integration Patterns

**Pattern: Agent → Memory Store**
```
OpenClaw (VPS) → EvermemOS MongoDB (Linux PC)
- Primary: Direct MongoDB connection
- Fallback: EvermemOS HTTP API
- Use case: Query memories, derive skills, track events
```

**Pattern: Service → Remote Database**
```
Web App (Server A) → PostgreSQL (Server B)
- Primary: PostgreSQL connection string
- Fallback: Read replica or cached data
- Use case: Production database access
```

**Pattern: Agent → Remote API**
```
Bot (Discord) → Custom API (VPS)
- Primary: HTTP REST API
- Fallback: Webhook notifications
- Use case: Command processing, data retrieval
```

### Guardrails

**Before Starting:**
- ✓ Verify both machines are reachable
- ✓ Check if target service is running
- ✓ Confirm network path (Tailscale, direct, VPN)
- ✓ Have credentials ready

**During Setup:**
- ✓ Test connectivity before installing dependencies
- ✓ Use virtual environments for Python packages
- ✓ Handle Tailscale authentication loops gracefully
- ✓ Create integration script with error handling
- ✓ Always configure fallback method

**After Setup:**
- ✓ Document connection details
- ✓ Set up monitoring/logging
- ✓ Test both primary and fallback methods
- ✓ Verify performance is acceptable

**Security:**
- ⚠️ Use environment variables for credentials (not hardcoded)
- ⚠️ Prefer key-based SSH over password auth
- ⚠️ Use TLS/SSL for production connections
- ⚠️ Restrict access with firewall rules if needed

### Troubleshooting

**Issue: Network timeout**
```bash
# Check if target is reachable
ping TARGET_IP

# Check if port is open
nc -zv TARGET_IP PORT

# Check Tailscale status
tailscale status
```

**Issue: Authentication failed**
```bash
# Verify credentials
ssh USER@TARGET_HOST "mongo --eval 'db.auth(\"user\",\"pass\")'"

# Check user permissions
ssh USER@TARGET_HOST "mongo admin --eval 'db.getUsers()'"
```

**Issue: Connection works manually but not in script**
```bash
# Check Python environment
ssh USER@SOURCE_HOST "which python3"

# Verify imports
ssh USER@SOURCE_HOST "~/.venv/bin/python3 -c 'import pymongo; print(pymongo.__version__)'"

# Test connection from Python
ssh USER@SOURCE_HOST "~/.venv/bin/python3 -c 'from pymongo import MongoClient; print(MongoClient(\"URI\").list_database_names())'"
```

**Issue: High latency**
- Check network path (is it going through VPN unnecessarily?)
- Consider caching frequently accessed data locally
- Use connection pooling for database connections
- Set appropriate timeouts (don't wait forever)

### Advanced: Automated Health Checks

Create monitoring script:
```bash
#!/bin/bash
# Check integration health every 5 minutes

PRIMARY_OK=$(~/integration_script.py --test-primary 2>&1 | grep -c "✓")
FALLBACK_OK=$(~/integration_script.py --test-fallback 2>&1 | grep -c "✓")

if [ $PRIMARY_OK -eq 0 ] && [ $FALLBACK_OK -eq 0 ]; then
    echo "ALERT: Both primary and fallback failed!"
    # Send notification
fi
```

Add to crontab:
```bash
*/5 * * * * ~/check_integration.sh >> ~/integration_health.log 2>&1
```

---
*Generated by /reflect-skills from cross-machine integration session patterns*
