import asyncio
import os
from typing import Annotated
from dotenv import load_dotenv
from fastmcp import FastMCP

# Fix import path - adjust based on your actual FastMCP version
try:
    from fastmcp.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
except ImportError:
    from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair

# Use FastMCP's error classes if available, fallback to mcp
try:
    from fastmcp import ErrorData, McpError
    from fastmcp.types import INVALID_PARAMS, INTERNAL_ERROR
except ImportError:
    from mcp import ErrorData, McpError
    from mcp.types import INVALID_PARAMS, INTERNAL_ERROR

from mcp.server.auth.provider import AccessToken
from pydantic import Field
import httpx

load_dotenv()

# ===== env / assertions =====
TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# ===== Auth provider =====
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# ===== ENABLE STATELESS MODE =====
mcp = FastMCP(
    "Meme Fetcher MCP Server",  # Updated server name
    auth=SimpleBearerAuthProvider(TOKEN),
    stateless_http=True
)

@mcp.tool
async def about() -> dict:
    return {"name": "MemeMania", "description": "A server which gives you latest trending memes from reddit"}

# ===== validate tool =====
@mcp.tool
async def validate() -> str:
    return MY_NUMBER

# ===== Meme Fetcher Tool =====
async def fetch_memes(count: int = 3) -> list[dict]:
    """Fetch trending memes from the Meme API"""
    url = f"https://meme-api.com/gimme/{count}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            if response.status_code != 200:
                return []
            
            data = response.json()
            if not data.get("memes"):
                return []
            
            return [
                {
                    "title": meme["title"],
                    "url": meme["url"],
                    "subreddit": meme["subreddit"],
                    "nsfw": meme["nsfw"],
                    "post_link": meme["postLink"]
                }
                for meme in data["memes"]
            ]
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Meme API error: {str(e)}"
            ))

@mcp.tool(description="Fetch trending memes from Reddit")
async def get_memes(
    count: Annotated[int, Field(description="Number of memes to fetch", ge=1, le=5)] = 3
) -> dict:
    """
    Returns trending memes with titles, image URLs, and subreddit sources.
    Automatically filters NSFW content.
    """
    memes = await fetch_memes(count)
    
    # Filter NSFW memes if needed
    safe_memes = [m for m in memes if not m["nsfw"]]
    
    # If filtering removed all memes, try again
    if not safe_memes and memes:
        safe_memes = await fetch_memes(count)
        safe_memes = [m for m in safe_memes if not m["nsfw"]]
    
    return {
        "memes": safe_memes[:count],
        "count": len(safe_memes[:count])
    }

# ===== run server =====
async def main():
    print("🚀 Starting Meme Fetcher MCP server in STATELESS mode on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())
