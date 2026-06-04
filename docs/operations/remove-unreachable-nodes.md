# Removing Unreachable Nodes from AutoBot Fleet

## Problem

When provision runs log warnings about unreachable nodes:

\`\`\`
WARNING: Node 172.16.168.26 (172.16.168.26) is unreachable -- skipping (not enrolled?)
ERROR! Specified inventory, host pattern and/or --limit leaves us with no hosts to target.
\`\`\`

This occurs when a node exists in the SLM database but is not actually enrolled or reachable.

## Root Cause

The setup wizard inventory generation reads from the \`nodes\` table. When a node record exists but the node itself is not properly enrolled, Ansible attempts to target it during provision runs, causing warnings.

## Solution

### Step 1: List Unreachable Nodes

SSH to the SLM server and run the diagnostic script:

\`\`\`bash
cd /opt/autobot/autobot-slm-backend
source venv/bin/activate

# List all unreachable nodes
python scripts/remove_orphaned_node.py --list-unreachable --api-url http://localhost:8000
\`\`\`

### Step 2: Remove the Orphaned Node

\`\`\`bash
# Remove by IP
python scripts/remove_orphaned_node.py --ip 172.16.168.26 --api-url http://localhost:8000

# Or remove by node ID (from Step 1 output)
python scripts/remove_orphaned_node.py --node-id <node-id> --api-url http://localhost:8000 --force
\`\`\`

### Step 3: Verify

Run a provision operation and confirm the warning no longer appears in \`/var/log/autobot/ansible.log\`.

## Alternative: Direct Database Cleanup

If the SLM API is unavailable:

\`\`\`sql
-- Find the node
SELECT node_id, hostname, ip_address FROM nodes WHERE ip_address = '172.16.168.26';

-- Delete it (cascades to related tables)
DELETE FROM nodes WHERE ip_address = '172.16.168.26';
\`\`\`

## Related Issues

- GitHub #9285: Node 172.16.168.26 warnings on every provision run
- PR #9289: Added remove_orphaned_node.py script

## Prevention

When decommissioning nodes, always remove them via:
- SLM UI: Node Management → Delete Node
- API: \`DELETE /api/nodes/{node_id}\`
- Script: \`remove_orphaned_node.py\`

Do not manually delete from Ansible inventory files — the dynamic inventory is generated from the database.
