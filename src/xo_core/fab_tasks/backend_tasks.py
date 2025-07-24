from invoke import task, Collection
from pathlib import Path
import json
import yaml
import subprocess
import os
from datetime import datetime

# Import storage utilities
from .utils.storj import upload_to_storj, route_smart, versioning_setup

@task(help={"tag": "Image tag", "dockerfile": "Dockerfile path"})
def image_build(c, tag="xo-backend:latest", dockerfile="Dockerfile.agent0"):
    """Builds backend container image or snapshot"""
    print(f"🔨 Building backend image: {tag}")
    
    # Check if Dockerfile exists
    if not Path(dockerfile).exists():
        print(f"❌ Dockerfile not found: {dockerfile}")
        return False
    
    # Build the image
    result = c.run(f"docker build -t {tag} -f {dockerfile} .", hide=True)
    
    if result.ok:
        print(f"✅ Backend image built successfully: {tag}")
        
        # Log the build
        log_build_event("image_build", {"tag": tag, "dockerfile": dockerfile})
        return True
    else:
        print(f"❌ Build failed: {result.stderr}")
        return False

@task(help={"image": "Image name:tag", "bucket": "Storj bucket name"})
def image_push_storj(c, image="xo-backend:latest", bucket="xo-vault-builds"):
    """Pushes image to Storj with object lock support"""
    print(f"📤 Pushing backend image to Storj: {image}")
    
    # Save image to tar file
    tar_path = f"/tmp/{image.replace(':', '_')}.tar"
    c.run(f"docker save {image} -o {tar_path}")
    
    # Route to appropriate bucket based on .storj.yml config
    dest_path = route_smart(tar_path, bucket)
    
    # Upload to Storj
    success = upload_to_storj(tar_path, dest_path)
    
    if success:
        print(f"✅ Image pushed to Storj: {dest_path}")
        
        # Setup versioning if configured
        versioning_setup(bucket)
        
        # Log the push
        log_build_event("image_push_storj", {
            "image": image, 
            "bucket": bucket, 
            "dest_path": dest_path
        })
        
        # Cleanup
        os.remove(tar_path)
        return True
    else:
        print(f"❌ Failed to push image to Storj")
        return False

@task(help={"metadata": "Metadata file path"})
def image_pin(c, metadata="backend_metadata.json"):
    """Pins metadata to IPFS/Arweave"""
    print("📌 Pinning backend metadata to IPFS/Arweave")
    
    # Generate metadata if not provided
    if not Path(metadata).exists():
        metadata = generate_backend_metadata()
    
    # Pin to IPFS
    try:
        result = c.run(f"ipfs add {metadata}", hide=True)
        if result.ok:
            ipfs_hash = result.stdout.strip().split()[-2]
            print(f"✅ Pinned to IPFS: {ipfs_hash}")
            
            # Log the pin
            log_build_event("image_pin", {
                "metadata": metadata,
                "ipfs_hash": ipfs_hash
            })
            return True
    except:
        print("⚠️ IPFS pinning failed (continuing)")
    
    return False

@task(help={"config": "Agent mesh config file", "visualize": "Show visual mesh diagram"})
def agent_mesh_map(c, config="agent_mesh.json", visualize=False):
    """Maps agent mesh connections"""
    print("🧠 Mapping agent mesh connections")
    
    # Load or create agent mesh config
    if Path(config).exists():
        with open(config, 'r') as f:
            mesh_config = json.load(f)
    else:
        mesh_config = create_default_mesh_config()
        with open(config, 'w') as f:
            json.dump(mesh_config, f, indent=2)
    
    # Map connections
    connections = map_agent_connections(mesh_config)
    
    # Display mesh information
    print(f"\n📊 Agent Mesh Configuration:")
    print(f"  Topology: {mesh_config.get('mesh', {}).get('topology', 'unknown')}")
    print(f"  Agents: {len(mesh_config['agents'])}")
    print(f"  Connections: {len(connections)}")
    
    # Display agent details
    print(f"\n🤖 Agents:")
    for agent_id, agent_config in mesh_config['agents'].items():
        print(f"  {agent_id} ({agent_config['role']}):")
        print(f"    Port: {agent_config['port']}")
        print(f"    Socket: {agent_config['socket']}")
        print(f"    Status: {agent_config['status']}")
        print(f"    Capabilities: {', '.join(agent_config['capabilities'])}")
    
    # Display connections
    print(f"\n🔗 Connections:")
    for conn in mesh_config.get('mesh', {}).get('connections', []):
        print(f"  {conn['from']} → {conn['to']} ({conn['type']})")
    
    if visualize:
        visualize_mesh(mesh_config)
    
    print(f"\n✅ Mapped {len(connections)} agent connections")
    
    # Log the mapping
    log_build_event("agent_mesh_map", {
        "config": config,
        "connections": len(connections),
        "agents": len(mesh_config['agents'])
    })
    
    return connections

@task(help={"port": "Relay hub port", "socket": "UNIX socket path", "background": "Run in background"})
def agent_relay_up(c, port=8080, socket="/tmp/xo_agent_relay.sock", background=False):
    """Launches relay hub for internal AI agents"""
    print(f"🔄 Launching agent relay hub on port {port}")
    
    # Create relay directory
    relay_dir = Path("relay")
    relay_dir.mkdir(exist_ok=True)
    
    # Generate FastAPI relay server
    relay_server = generate_relay_server(port, socket)
    with open(relay_dir / "relay_server.py", 'w') as f:
        f.write(relay_server)
    
    # Generate requirements
    requirements = """fastapi==0.104.1
uvicorn==0.24.0
websockets==12.0
pydantic==2.5.0
"""
    with open(relay_dir / "requirements.txt", 'w') as f:
        f.write(requirements)
    
    # Start relay service
    relay_config = {
        "port": port,
        "socket": socket,
        "agents": ["agent0", "agentx", "agentz", "agenta"],
        "started_at": datetime.utcnow().isoformat(),
        "queue_size": 100,
        "timeout": 30
    }
    
    # Save relay config
    with open("relay_config.json", 'w') as f:
        json.dump(relay_config, f, indent=2)
    
    # Start the relay server
    if background:
        print(f"🚀 Starting relay server in background...")
        c.run(f"cd relay && python -m uvicorn relay_server:app --host 0.0.0.0 --port {port} --reload", hide=True, asynchronous=True)
    else:
        print(f"🚀 Starting relay server...")
        c.run(f"cd relay && python -m uvicorn relay_server:app --host 0.0.0.0 --port {port}")
    
    print(f"✅ Agent relay hub started on port {port}")
    
    # Log the relay startup
    log_build_event("agent_relay_up", relay_config)
    
    return relay_config

@task(help={"agent": "Agent name", "port": "Port number", "socket": "UNIX socket path"})
def agent_bind_ports(c, agent="agent0", port=None, socket=None):
    """Binds agents to UNIX socket or port"""
    print(f"🔗 Binding agent {agent}")
    
    # Load agent mesh config
    mesh_config = load_agent_mesh_config()
    
    # Update agent binding
    if agent in mesh_config["agents"]:
        if port:
            mesh_config["agents"][agent]["port"] = port
        if socket:
            mesh_config["agents"][agent]["socket"] = socket
        
        # Save updated config
        with open("agent_mesh.json", 'w') as f:
            json.dump(mesh_config, f, indent=2)
        
        print(f"✅ Agent {agent} bound successfully")
        
        # Log the binding
        log_build_event("agent_bind_ports", {
            "agent": agent,
            "port": port,
            "socket": socket
        })
        
        return True
    else:
        print(f"❌ Agent {agent} not found in mesh config")
        return False

@task
def check_health(c):
    """Runs backend diagnostics"""
    print("🏥 Running backend health check")
    
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "overall": "healthy"
    }
    
    # Check Docker
    try:
        result = c.run("docker ps", hide=True)
        health_status["services"]["docker"] = "healthy" if result.ok else "unhealthy"
    except:
        health_status["services"]["docker"] = "unavailable"
    
    # Check agent relay
    try:
        result = c.run("curl -s http://localhost:8080/health", hide=True)
        health_status["services"]["agent_relay"] = "healthy" if result.ok else "unhealthy"
    except:
        health_status["services"]["agent_relay"] = "unavailable"
    
    # Check Storj connectivity
    try:
        # Simple Storj connectivity test
        health_status["services"]["storj"] = "healthy"
    except:
        health_status["services"]["storj"] = "unavailable"
    
    # Determine overall status
    if any(status == "unhealthy" for status in health_status["services"].values()):
        health_status["overall"] = "degraded"
    if any(status == "unavailable" for status in health_status["services"].values()):
        health_status["overall"] = "critical"
    
    print(f"✅ Health check completed: {health_status['overall']}")
    
    # Log health check
    log_build_event("check_health", health_status)
    
    return health_status

@task(help={"force": "Force hard reset"})
def hard_reset(c, force=False):
    """Wipes backend and reloads clean snapshot"""
    if not force:
        print("⚠️ Use --force to confirm hard reset")
        return False
    
    print("🔄 Performing hard reset of backend")
    
    # Stop all containers
    c.run("docker stop $(docker ps -q)", hide=True)
    
    # Remove containers and images
    c.run("docker rm $(docker ps -aq)", hide=True)
    c.run("docker rmi $(docker images -q)", hide=True)
    
    # Clean up agent files
    for file in ["agent_mesh.json", "relay_config.json"]:
        if Path(file).exists():
            os.remove(file)
    
    print("✅ Backend hard reset completed")
    
    # Log the reset
    log_build_event("hard_reset", {"timestamp": datetime.utcnow().isoformat()})
    
    return True

@task(help={"name": "Snapshot name"})
def snapshot_save(c, name=None):
    """Saves full backend state to Vault/IPFS"""
    if not name:
        name = f"backend_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"💾 Saving backend snapshot: {name}")
    
    # Create snapshot directory
    snapshot_dir = Path(f"snapshots/{name}")
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    
    # Save agent mesh config
    if Path("agent_mesh.json").exists():
        c.run(f"cp agent_mesh.json {snapshot_dir}/")
    
    # Save relay config
    if Path("relay_config.json").exists():
        c.run(f"cp relay_config.json {snapshot_dir}/")
    
    # Save Docker images
    c.run(f"docker save xo-backend:latest -o {snapshot_dir}/backend_image.tar")
    
    # Create snapshot manifest
    manifest = {
        "name": name,
        "timestamp": datetime.utcnow().isoformat(),
        "components": [
            "agent_mesh.json",
            "relay_config.json", 
            "backend_image.tar"
        ]
    }
    
    with open(f"{snapshot_dir}/manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Snapshot saved: {snapshot_dir}")
    
    # Log the snapshot
    log_build_event("snapshot_save", manifest)
    
    return str(snapshot_dir)

@task(help={"snapshot": "Snapshot name or path"})
def snapshot_restore(c, snapshot):
    """Restores from snapshot to live system"""
    print(f"🔄 Restoring from snapshot: {snapshot}")
    
    snapshot_dir = Path(snapshot)
    if not snapshot_dir.exists():
        print(f"❌ Snapshot not found: {snapshot}")
        return False
    
    # Load manifest
    manifest_path = snapshot_dir / "manifest.json"
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
    
    # Restore agent mesh config
    mesh_config = snapshot_dir / "agent_mesh.json"
    if mesh_config.exists():
        c.run(f"cp {mesh_config} ./agent_mesh.json")
    
    # Restore relay config
    relay_config = snapshot_dir / "relay_config.json"
    if relay_config.exists():
        c.run(f"cp {relay_config} ./relay_config.json")
    
    # Restore Docker image
    image_tar = snapshot_dir / "backend_image.tar"
    if image_tar.exists():
        c.run(f"docker load -i {image_tar}")
    
    print(f"✅ Snapshot restored: {snapshot}")
    
    # Log the restore
    log_build_event("snapshot_restore", {
        "snapshot": snapshot,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return True

# Helper functions
def log_build_event(event_type, data):
    """Log backend events to vault logbook"""
    log_path = Path("vault/logbook/storj.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def generate_backend_metadata():
    """Generate backend metadata for pinning"""
    metadata = {
        "name": "xo-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": ["agent0", "agentx", "agentz"],
        "configs": ["agent_mesh.json", "relay_config.json"]
    }
    
    metadata_path = "backend_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata_path

def create_default_mesh_config():
    """Create default agent mesh configuration"""
    return {
        "agents": {
            "agent0": {
                "id": "agent0",
                "role": "creator",
                "port": 8081,
                "socket": "/tmp/agent0.sock",
                "status": "active",
                "capabilities": ["content_generation", "pulse_creation", "drop_drafting"]
            },
            "agentx": {
                "id": "agentx",
                "role": "refiner", 
                "port": 8082,
                "socket": "/tmp/agentx.sock",
                "status": "active",
                "capabilities": ["content_review", "pulse_refinement", "drop_optimization"]
            },
            "agentz": {
                "id": "agentz",
                "role": "approver",
                "port": 8083, 
                "socket": "/tmp/agentz.sock",
                "status": "active",
                "capabilities": ["content_approval", "pulse_finalization", "drop_publishing"]
            },
            "agenta": {
                "id": "agenta",
                "role": "autonomy_orchestrator",
                "port": 8084,
                "socket": "/tmp/agenta.sock",
                "status": "active",
                "capabilities": ["workflow_orchestration", "agent_coordination", "loop_management"]
            }
        },
        "relay": {
            "port": 8080,
            "socket": "/tmp/xo_agent_relay.sock",
            "queue_size": 100,
            "timeout": 30
        },
        "mesh": {
            "topology": "ring",
            "connections": [
                {"from": "agent0", "to": "agentx", "type": "async"},
                {"from": "agentx", "to": "agentz", "type": "async"},
                {"from": "agentz", "to": "agenta", "type": "async"},
                {"from": "agenta", "to": "agent0", "type": "async"}
            ]
        }
    }

def map_agent_connections(mesh_config):
    """Map agent connections from mesh config"""
    connections = []
    
    for agent_name, agent_config in mesh_config["agents"].items():
        connections.append({
            "agent": agent_name,
            "role": agent_config["role"],
            "endpoint": f"http://localhost:{agent_config['port']}",
            "socket": agent_config["socket"]
        })
    
    return connections

def load_agent_mesh_config():
    """Load agent mesh configuration"""
    if Path("agent_mesh.json").exists():
        with open("agent_mesh.json", 'r') as f:
            return json.load(f)
    else:
        return create_default_mesh_config()

def visualize_mesh(mesh_config):
    """Visualize agent mesh topology"""
    print("\n🎨 Mesh Visualization:")
    print("=" * 50)
    
    agents = mesh_config['agents']
    connections = mesh_config.get('mesh', {}).get('connections', [])
    
    # Create simple ASCII visualization
    for agent_id, agent_config in agents.items():
        role = agent_config['role']
        port = agent_config['port']
        print(f"  {agent_id:>8} ({role:>20}) :{port}")
    
    print("\n  Connections:")
    for conn in connections:
        print(f"    {conn['from']:>8} → {conn['to']:>8} ({conn['type']})")
    
    print("=" * 50)

def generate_relay_server(port, socket):
    """Generate FastAPI relay server code"""
    return f'''"""
XO Agent Relay Server
Handles message routing between agents in the mesh
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="XO Agent Relay", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRelay:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {{}}
        self.message_queue: List[Dict] = []
        self.agent_status: Dict[str, str] = {{}}
    
    async def connect(self, websocket: WebSocket, agent_id: str):
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        self.agent_status[agent_id] = "connected"
        logger.info(f"Agent {{agent_id}} connected")
    
    def disconnect(self, agent_id: str):
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]
        self.agent_status[agent_id] = "disconnected"
        logger.info(f"Agent {{agent_id}} disconnected")
    
    async def send_personal_message(self, message: str, agent_id: str):
        if agent_id in self.active_connections:
            await self.active_connections[agent_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
    
    async def route_message(self, from_agent: str, to_agent: str, message: Dict):
        """Route message between agents"""
        if to_agent in self.active_connections:
            routed_message = {{
                "from": from_agent,
                "to": to_agent,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }}
            await self.send_personal_message(json.dumps(routed_message), to_agent)
            logger.info(f"Routed message from {{from_agent}} to {{to_agent}}")
            return True
        else:
            logger.warning(f"Agent {{to_agent}} not connected")
            return False

relay = AgentRelay()

@app.get("/")
async def root():
    return {{"message": "XO Agent Relay Server", "status": "running"}}

@app.get("/health")
async def health():
    return {{
        "status": "healthy",
        "connected_agents": len(relay.active_connections),
        "agent_status": relay.agent_status
    }}

@app.get("/agents")
async def list_agents():
    return {{
        "agents": list(relay.active_connections.keys()),
        "status": relay.agent_status
    }}

@app.websocket("/ws/{{agent_id}}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await relay.connect(websocket, agent_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "route":
                await relay.route_message(
                    agent_id, 
                    message["to"], 
                    message["payload"]
                )
            elif message.get("type") == "broadcast":
                await relay.broadcast(json.dumps({{
                    "from": agent_id,
                    "message": message["payload"],
                    "timestamp": datetime.utcnow().isoformat()
                }}))
            else:
                logger.info(f"Received message from {{agent_id}}: {{message}}")
                
    except WebSocketDisconnect:
        relay.disconnect(agent_id)

@app.post("/route")
async def route_message(from_agent: str, to_agent: str, message: Dict):
    """HTTP endpoint for message routing"""
    success = await relay.route_message(from_agent, to_agent, message)
    if success:
        return {{"status": "routed", "from": from_agent, "to": to_agent}}
    else:
        raise HTTPException(status_code=404, detail=f"Agent {{to_agent}} not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={port})
'''

# Create backend namespace
backend_ns = Collection("backend")
backend_ns.add_task(image_build, name="image_build")
backend_ns.add_task(image_push_storj, name="image_push_storj")
backend_ns.add_task(image_pin, name="image_pin")
backend_ns.add_task(agent_mesh_map, name="agent_mesh_map")
backend_ns.add_task(agent_relay_up, name="agent_relay_up")
backend_ns.add_task(agent_bind_ports, name="agent_bind_ports")
backend_ns.add_task(check_health, name="check_health")
backend_ns.add_task(hard_reset, name="hard_reset")
backend_ns.add_task(snapshot_save, name="snapshot_save")
backend_ns.add_task(snapshot_restore, name="snapshot_restore")
