# MemeMania MCP Server

A stateless MCP server built with [FastMCP](https://pypi.org/project/fastmcp/) that fetches trending memes from the [Meme API](https://github.com/D3vd/Meme_Api).  
Supports Bearer Token authentication and filters NSFW content automatically.

---

## 🚀 Features

- Stateless MCP server for easy deployment
- Bearer Token–based authentication
- Fetches trending memes with title, image URL, subreddit, and post link
- Filters NSFW content automatically
- Asynchronous `httpx` for fast API calls
- Error handling with MCP standard error codes

---

## 📦 Requirements

- Python **3.10+**
- [Meme API](https://github.com/D3vd/Meme_Api) (no API key required)
- An authentication token for your MCP server (`AUTH_TOKEN`)

---

## ⚙️ Setup

#### 1 Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
```

#### 2 Install dependencies
```bash
pip install -r requirements.txt
```
#### 3 Set up .env file
```bash
AUTH_TOKEN=your_auth_token
MY_NUMBER=91
```

#### 4 Run the MCP Server
```bash
python main.py
```
get_memes
Fetches trending memes from Reddit via Meme API.

Example input:

json
Copy code
{
  "count": 3
}
### Example output:

```bash
{
  "memes": [
    {
      "title": "Funny meme title",
      "url": "https://i.redd.it/memeimage.jpg",
      "subreddit": "memes",
      "nsfw": false,
      "post_link": "https://redd.it/abc123"
    }
  ],
  "count": 1
}
```
## 🛡 Authentication
This server uses Bearer Token authentication.
Include the Authorization: Bearer <AUTH_TOKEN> header in every request.
