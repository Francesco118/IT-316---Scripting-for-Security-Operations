import aiohttp
import asyncio
from aiohttp import web

# In-memory storage for connected clients and commands
clients = {}
commands = {}

async def register_client(request):
    """Registers a new client."""
    data = await request.json()
    client_id = data.get("client_id")
    
    if not client_id:
        return web.json_response({"error": "Missing client_id"}, status=400)

    clients[client_id] = {"status": "connected"}
    return web.json_response({"message": "Client registered", "client_id": client_id})

async def get_command(request):
    """Sends a command to a client."""
    client_id = request.match_info.get("client_id")
    
    if client_id not in clients:
        return web.json_response({"error": "Client not found"}, status=404)

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

app = web.Application()
app.add_routes([
    web.post("/register", register_client),
    web.get("/command/{client_id}", get_command),
    web.post("/result", post_result),
    web.post("/issue_command", issue_command)
])

if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8080)
