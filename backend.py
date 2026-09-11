import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any

# Import class dari auto_like.py
from auto_like import AccountManager, CookiesManager, FacebookAutoLike, CONFIG

app = FastAPI(title="Auto-Like Bot API")

# Setup CORS agar bisa diakses React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi Manager
account_manager = AccountManager(CONFIG.get("accounts_dir", "./accounts"))
cookies_manager = CookiesManager(CONFIG.get("cookies_dir", "./cookies"))

class AccountCreate(BaseModel):
    name: str
    email: str
    password: str

class CookiesCreate(BaseModel):
    name: str
    cookies: List[Dict[str, Any]]

class ConfigUpdate(BaseModel):
    target_url: str
    max_likes: int
    min_delay: int
    max_delay: int
    headless: bool

@app.get("/api/accounts")
def get_accounts():
    accounts = account_manager.get_all_accounts()
    for acc in accounts:
        # Check if cookies exist
        has_cookies = cookies_manager.load_cookies(acc["name"]) is not None
        acc["has_cookies"] = has_cookies
    return accounts

@app.post("/api/accounts")
def add_account(data: AccountCreate):
    existing = account_manager.get_account(data.name)
    if existing:
        raise HTTPException(status_code=400, detail="Account with this name already exists")
    
    account = account_manager.add_account(data.name, data.email, data.password)
    if not account:
        raise HTTPException(status_code=400, detail="Email might already be in use")
    return {"message": "Account added successfully", "account": account}

@app.delete("/api/accounts/{name}")
def delete_account(name: str):
    success = account_manager.delete_account(name)
    if not success:
        raise HTTPException(status_code=404, detail="Account not found")
    cookies_manager.delete_cookies(name)
    return {"message": "Account deleted"}

@app.post("/api/cookies")
def set_cookies(data: CookiesCreate):
    account = account_manager.get_account(data.name)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if not cookies_manager.validate_cookies(data.cookies):
        raise HTTPException(status_code=400, detail="Invalid cookies format or missing required cookies (c_user, xs, fr, datr)")
    
    cookies_manager.save_cookies(data.name, data.cookies)
    return {"message": "Cookies saved successfully"}

@app.get("/api/config")
def get_config():
    return CONFIG

@app.post("/api/config")
def update_config(data: ConfigUpdate):
    CONFIG["target_url"] = data.target_url
    CONFIG["max_likes"] = data.max_likes
    CONFIG["min_delay"] = data.min_delay
    CONFIG["max_delay"] = data.max_delay
    CONFIG["headless"] = data.headless
    return {"message": "Config updated", "config": CONFIG}

@app.get("/api/results")
def get_results():
    if os.path.exists("results.json"):
        try:
            with open("results.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

@app.post("/api/run")
def run_bot():
    if not CONFIG.get("target_url"):
        raise HTTPException(status_code=400, detail="Target URL is empty")
    
    # Karena bot berjalan lama (blocking), dalam produksi sebaiknya gunakan BackgroundTasks / Celery
    # Namun untuk simple wrapper, kita kembalikan respons awal, lalu jalankan di thread terpisah.
    import threading
    
    def run_task():
        bot = FacebookAutoLike(CONFIG)
        # Hack untuk menangkap output log jika perlu: 
        # Untuk simple implementasi, log akan ke console backend
        bot.run()

    thread = threading.Thread(target=run_task)
    thread.start()
    
    return {"message": "Bot started in background. Check terminal for logs."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
