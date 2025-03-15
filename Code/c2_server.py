import aiohttp
import asyncio
from aiohttp import web
import json
import time
import os

# In-memory storage for connected clients and commands
clients = {}
commands = {}

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def register_client(request):
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
    
    if client_id not in clients: #check if client is registered
        return web.json_response({"error": "Client not found"}, status=404) #if client is not registered, return error

    if client_id not in commands:
        return web.json_response({"error": "Client not found"}, status=404) #if client is registered but no commands are present
    
    if commands[client_id]:
        return web.json_response({"command": commands[client_id].pop(0)}) #if client is registered and commands are present, return command
    
    return web.json_response({"command": None})

#Receive results from clients
async def post_result(request):
    """Receives results from clients."""
    data = await request.json()
    client_id = data.get("client_id")
    result = data.get("result")

    if not client_id or not result:
        return web.json_response({"error": "Missing data"}, status=400)

    print(f"Received result from {client_id}: {result}")
    return web.json_response({"message": "Result received"})

#Issue command to a specific client
async def issue_command(request):
    """Issues a command to a specific client."""
    data = await request.json()
    client_id = data.get("client_id")
    command = data.get("command")

#Check if client_id and command are present
    if not client_id or not command:
        return web.json_response({"error": "Missing data"}, status=400)
#Check if client_id is registered
    commands[client_id] = command
    return web.json_response({"message": f"Command '{command}' sent to {client_id}"}) #Return message to server - command sent to client

#Upload file to client
async def upload_file(request):
    """Handles file upload requests from clients."""
    data = await request.json()
    client_id = data.get("client_id")
    file_path = data.get("file_path")

    if not client_id or not file_path:
        return web.json_response({"error": "Missing data"}, status=400)

    if not os.path.exists(file_path):
        return web.json_response({"error": "File not found"}, status=404)

    with open(file_path, 'rb') as f:
        file_data = f.read()

    return web.json_response({"file_data": file_data.decode('latin1')})

async def index(request):
    """Serve the HTML interface on the root URL."""
    try:
        with open('interface.html', 'r') as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type='text/html')
    except FileNotFoundError:
        return web.Response(text="HTML interface file not found. Please create interface.html", 
                           content_type="text/plain")


#Main function
app = web.Application()

# Configure CORS to allow browser requests
async def cors_middleware(app, handler):
    async def middleware_handler(request):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    return middleware_handler

app.middlewares.append(cors_middleware)

app.add_routes([
    web.post("/register", register_client),
    web.get("/command/{client_id}", get_command),
    web.post("/result", post_result),
    web.post("/issue_command", issue_command),
    web.post("/upload_file", upload_file),
    web.post("/upload", upload_file),  # Add this route for file upload
    web.get("/download/{filename}", download_file)  # Add this route for file download
])

if __name__ == "__main__":
    web.run_app(app, host="localhost", port=8080)
