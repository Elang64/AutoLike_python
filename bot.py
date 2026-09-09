"""
Facebook Auto-Like Bot v8 - Integrated dengan Cookies Manager
- Auto-load cookies dari file JSON
- Auto-login menggunakan cookies
- Like target post
"""

from playwright.sync_api import sync_playwright
import time
import random
import os
import json
import platform
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

# ═══════════════════════════════════════════════════════
# KONFIGURASI
# ═══════════════════════════════════════════════════════

CONFIG = {
    # Target URL
    "target_url": "https://www.facebook.com/share/p/18GMyxFajm/",
    
    # Batas like per akun
    "max_likes": 1,
    
    # Delay antar aksi (detik)
    "min_delay": 3,
    "max_delay": 8,
    
    # Delay antar akun (detik)
    "delay_between_accounts": (10, 20),
    
    # Path Chrome (auto-detect jika None)
    "chrome_path": None,
    
    # Mode headless
    "headless": False,
    
    # Folder untuk cookies dan data akun
    "cookies_dir": "./cookies",
    "accounts_dir": "./accounts",
}

# ═══════════════════════════════════════════════════════
# ACCOUNT MANAGER
# ═══════════════════════════════════════════════════════

class AccountManager:
    """Manage data akun"""
    
    def __init__(self, accounts_dir: str = "./accounts"):
        self.accounts_dir = Path(accounts_dir)
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self.accounts_file = self.accounts_dir / "accounts.json"
        self.load_accounts()
    
    def load_accounts(self):
        """Load data akun"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r") as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = []
        else:
            self.accounts = []
    
    def get_all_accounts(self) -> List[Dict]:
        """Get semua akun"""
        return self.accounts
    
    def get_account_with_cookies(self) -> List[Dict]:
        """Get akun yang memiliki cookies"""
        accounts_with_cookies = []
        
        for account in self.accounts:
            cookies_file = Path(CONFIG["cookies_dir"]) / f"{account['name']}_cookies.json"
            if cookies_file.exists():
                account["cookies_file"] = f"{account['name']}_cookies.json"
                accounts_with_cookies.append(account)
        
        return accounts_with_cookies

# ═══════════════════════════════════════════════════════
# COOKIES MANAGER
# ═══════════════════════════════════════════════════════

class CookiesManager:
    """Manage cookies"""
    
    def __init__(self, cookies_dir: str = "./cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
    
    def load_cookies(self, account_name: str) -> Optional[List[Dict]]:
        """Load cookies dari file"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        if not cookies_file.exists():
            print(f"❌ File cookies tidak ditemukan: {cookies_file}")
            return None
        
        try:
            with open(cookies_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            
            print(f"✅ Cookies loaded: {cookies_file}")
            return cookies
        except Exception as e:
            print(f"❌ Gagal load cookies: {e}")
            return None
    
    def validate_cookies(self, cookies: List[Dict]) -> bool:
        """Validasi cookies"""
        required = ["c_user", "xs", "fr", "datr"]
        cookie_names = [c.get("name") for c in cookies]
        
        missing = [r for r in required if r not in cookie_names]
        
        if missing:
            print(f"❌ Cookies wajib tidak ditemukan: {', '.join(missing)}")
            return False
        
        # Check expiry
        for cookie in cookies:
            if "expirationDate" in cookie and cookie["expirationDate"]:
                exp_date = datetime.fromtimestamp(cookie["expirationDate"])
                if exp_date < datetime.now():
                    print(f"⚠️ Cookie '{cookie['name']}' expired pada {exp_date}")
                    return False
        
        # Get user ID
        user_id = None
        for cookie in cookies:
            if cookie.get("name") == "c_user":
                user_id = cookie.get("value")
                break
        
        if user_id:
            print(f"✅ Cookies valid! User ID: {user_id}")
        else:
            print("✅ Cookies valid!")
        
        return True
    
    def format_for_playwright(self, cookies: List[Dict]) -> List[Dict]:
        """Format cookies untuk Playwright"""
        formatted = []
        
        for cookie in cookies:
            if not cookie.get("name") or not cookie.get("value"):
                continue
            
            formatted_cookie = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", ".facebook.com"),
                "path": cookie.get("path", "/"),
            }
            
            if "expirationDate" in cookie and cookie["expirationDate"]:
                formatted_cookie["expires"] = cookie["expirationDate"]
            
            if "secure" in cookie:
                formatted_cookie["secure"] = cookie["secure"]
            
            if "httpOnly" in cookie:
                formatted_cookie["httpOnly"] = cookie["httpOnly"]
            
            if "sameSite" in cookie and cookie["sameSite"]:
                same_site_map = {
                    "no_restriction": "None",
                    "lax": "Lax",
                    "strict": "Strict",
                    "unspecified": "Lax",
                }
                formatted_cookie["sameSite"] = same_site_map.get(
                    cookie["sameSite"], "Lax"
                )
            
            formatted.append(formatted_cookie)
        
        return formatted

# ═══════════════════════════════════════════════════════
# CHROME DETECTOR
# ═══════════════════════════════════════════════════════

def detect_chrome() -> Optional[str]:
    """Deteksi Chrome"""
    system = platform.system()
    
    paths = {
        "Windows": [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%/Google/Chrome/Application/chrome.exe"),
            os.path.expandvars(r"%PROGRAMFILES%/Google/Chrome/Application/chrome.exe"),
        ],
        "Darwin": [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
        ]
    }
    
    for path in paths.get(system, []):
        if os.path.exists(path):
            print(f"✅ Chrome: {path}")
            return path
    
    print("❌ Chrome tidak ditemukan!")
    return None

# ═══════════════════════════════════════════════════════
# FACEBOOK AUTO-LIKE BOT
# ═══════════════════════════════════════════════════════

class FacebookAutoLike:
    """Bot auto-like dengan cookies"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.cookies_manager = CookiesManager(config.get("cookies_dir", "./cookies"))
        self.account_manager = AccountManager(config.get("accounts_dir", "./accounts"))
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_account = None
    
    def log(self, msg: str, level: str = "INFO"):
        """Log"""
        t = datetime.now().strftime("%H:%M:%S")
        icons = {
            "INFO": "ℹ️",
            "OK": "✅",
            "WARN": "⚠️",
            "ERR": "❌",
            "COOKIE": "🍪",
            "LOGIN": "🔐",
        }
        
        account_name = ""
        if self.current_account:
            account_name = f"[{self.current_account.get('name', 'unknown')}] "
        
        print(f"[{t}] {account_name}{icons.get(level, 'ℹ️')} {msg}", flush=True)
    
    def wait(self, a: float, b: Optional[float] = None):
        """Delay"""
        if b is None:
            time.sleep(a)
        else:
            time.sleep(random.uniform(a, b))
    
    def setup_browser(self, account: Dict):
        """Setup browser dengan cookies"""
        self.log("Menyiapkan browser...", "INFO")
        
        chrome_path = self.config["chrome_path"] or detect_chrome()
        
        if not chrome_path:
            raise Exception("Chrome tidak ditemukan!")
        
        # Launch browser
        self.browser = self.playwright.chromium.launch(
            executable_path=chrome_path,
            headless=self.config["headless"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1366,768",
                "--disable-notifications",
            ],
        )
        
        # Buat context baru
        self.context = self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        self.page = self.context.new_page()
        
        # Anti-detection
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['id-ID', 'id', 'en-US', 'en']});
        """)
        
        # Inject cookies
        self.inject_cookies(account)
        
        self.log("Browser siap!", "OK")
    
    def inject_cookies(self, account: Dict):
        """Inject cookies"""
        account_name = account.get("name")
        cookies_file = account.get("cookies_file")
        
        if not cookies_file:
            cookies_file = f"{account_name}_cookies.json"
        
        # Load cookies
        cookies = self.cookies_manager.load_cookies(account_name)
        
        if not cookies:
            self.log(f"Gagal load cookies untuk {account_name}", "ERR")
            return
        
        # Validasi
        if not self.cookies_manager.validate_cookies(cookies):
            self.log("Cookies tidak valid!", "ERR")
            return
        
        # Format
        formatted_cookies = self.cookies_manager.format_for_playwright(cookies)
        
        # Inject
        try:
            self.context.add_cookies(formatted_cookies)
            self.log(f"✅ {len(formatted_cookies)} cookies di-inject", "COOKIE")
        except Exception as e:
            self.log(f"Gagal inject cookies: {e}", "ERR")
    
    def check_login(self) -> bool:
        """Check login status"""
        self.log("Memeriksa login...", "LOGIN")
        
        try:
            self.page.goto("https://www.facebook.com/", timeout=30000)
            self.wait(3, 5)
            
            current_url = self.page.url
            self.log(f"URL: {current_url}", "INFO")
            
            if "login" in current_url or "recover" in current_url:
                self.log("Redirect ke login, cookies invalid", "WARN")
                return False
            
            # Check indikator login
            indicators = [
                "a[aria-label*='Profil']",
                "a[aria-label*='Profile']",
                "div[aria-label*='Buat']",
                "div[aria-label*='Menu']",
                "[data-pagelet='LeftRail']",
                "a[href*='/messages/']",
            ]
            
            for indicator in indicators:
                try:
                    if self.page.locator(indicator).first.is_visible(timeout=2000):
                        self.log("✅ Login berhasil!", "OK")
                        return True
                except:
                    continue
            
            # Check form login
            try:
                if self.page.locator("#email").is_visible(timeout=2000):
                    self.log("Form login terlihat", "ERR")
                    return False
            except:
                pass
            
            self.log("Kemungkinan sudah login", "OK")
            return True
            
        except Exception as e:
            self.log(f"Error: {e}", "ERR")
            return False
    
    def find_like_buttons(self) -> List:
        """Cari tombol like"""
        selectors = [
            "div[aria-label='Like']",
            "div[aria-label='Suka']",
            "div[aria-label='Sukai']",
            "div[role='button'][aria-label='Like']",
            "div[role='button'][aria-label='Suka']",
            "div[role='button'][aria-label='Sukai']",
            "span:has-text('Like')",
            "span:has-text('Suka')",
            "span:has-text('Sukai')",
        ]
        
        buttons = []
        seen = set()
        
        for sel in selectors:
            try:
                elements = self.page.locator(sel).all()
                for el in elements:
                    try:
                        el_id = el.evaluate("el => el.outerHTML")
                        if el_id in seen:
                            continue
                        seen.add(el_id)
                        
                        cls = el.get_attribute("class") or ""
                        aria_label = el.get_attribute("aria-label") or ""
                        
                        if any(term in cls.lower() for term in ["liked", "active"]) or \
                           any(term in aria_label.lower() for term in ["tidak suka", "unlike", "berhenti"]):
                            continue
                        
                        buttons.append(el)
                    except:
                        continue
            except:
                continue
        
        return buttons
    
    def like_target_post(self) -> bool:
        """Like target post"""
        target_url = self.config["target_url"]
        self.log(f"Membuka target: {target_url}", "INFO")
        
        try:
            self.page.goto(target_url, timeout=30000)
            self.wait(5, 8)
        except:
            self.log("Timeout membuka target", "ERR")
            return False
        
        current_url = self.page.url
        self.log(f"URL target: {current_url}", "INFO")
        
        if "login" in current_url:
            self.log("Redirect ke login", "WARN")
            return False
        
        self.log("Mencari tombol Like...", "INFO")
        
        liked = 0
        scrolls = 0
        max_scrolls = 10
        
        while liked < self.config["max_likes"] and scrolls < max_scrolls:
            buttons = self.find_like_buttons()
            self.log(f"Ditemukan {len(buttons)} tombol Like", "INFO")
            
            if buttons:
                for btn in buttons:
                    if liked >= self.config["max_likes"]:
                        break
                    
                    try:
                        btn.scroll_into_view_if_needed()
                        self.wait(1, 2)
                        
                        btn.hover()
                        self.wait(0.5, 1.5)
                        
                        btn.click()
                        liked += 1
                        self.log(f"✅ Like berhasil! Total: {liked}", "OK")
                        break
                        
                    except Exception as e:
                        self.log(f"Gagal like: {e}", "WARN")
                        continue
            
            try:
                self.page.evaluate("window.scrollBy({top: 400 + Math.random()*300, behavior: 'smooth'})")
            except:
                pass
            
            self.wait(2, 4)
            scrolls += 1
        
        if liked > 0:
            self.log(f"✅ Berhasil like {liked} postingan!", "OK")
            return True
        else:
            self.log("Tidak berhasil like", "ERR")
            self.page.screenshot(path="debug_no_like.png")
            return False
    
    def run_account(self, account: Dict) -> bool:
        """Run bot untuk satu akun"""
        self.current_account = account
        
        try:
            self.log("=" * 50, "INFO")
            self.log(f"Memproses: {account.get('name', 'unknown')}", "INFO")
            self.log("=" * 50, "INFO")
            
            self.setup_browser(account)
            
            if not self.check_login():
                self.log("Login gagal", "ERR")
                return False
            
            success = self.like_target_post()
            return success
            
        except Exception as e:
            self.log(f"Error: {e}", "ERR")
            return False
            
        finally:
            self.log("Menutup browser...", "INFO")
            if self.browser:
                self.browser.close()
    
    def run(self):
        """Run bot untuk semua akun"""
        # Load akun yang punya cookies
        accounts = self.account_manager.get_account_with_cookies()
        
        if not accounts:
            self.log("Tidak ada akun dengan cookies!", "ERR")
            self.log("Jalankan cookies_manager.py dulu untuk input cookies", "WARN")
            return
        
        self.log(f"Ditemukan {len(accounts)} akun dengan cookies", "INFO")
        
        try:
            self.playwright = sync_playwright().start()
            
            results = []
            
            for i, account in enumerate(accounts, 1):
                self.log(f"\n{'='*50}", "INFO")
                self.log(f"Akun {i}/{len(accounts)}", "INFO")
                self.log(f"{'='*50}", "INFO")
                
                success = self.run_account(account)
                
                results.append({
                    "account": account.get("name"),
                    "email": account.get("email", "unknown"),
                    "success": success,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                
                # Delay antar akun
                if i < len(accounts):
                    delay = random.uniform(*self.config["delay_between_accounts"])
                    self.log(f"Jeda {delay:.0f} detik...", "INFO")
                    time.sleep(delay)
            
            # Summary
            self.log(f"\n{'='*50}", "INFO")
            self.log("RINGKASAN HASIL:", "INFO")
            self.log(f"{'='*50}", "INFO")
            
            success_count = 0
            for result in results:
                status = "✅" if result["success"] else "❌"
                if result["success"]:
                    success_count += 1
                self.log(f"{status} {result['account']} ({result['email']})", "INFO")
            
            self.log(f"\nTotal berhasil: {success_count}/{len(results)}", "INFO")
            
            # Simpan hasil
            with open("results.json", "w") as f:
                json.dump(results, f, indent=2)
            
            self.log("Hasil disimpan ke results.json", "OK")
            
        except Exception as e:
            self.log(f"Fatal error: {e}", "ERR")
        finally:
            if self.playwright:
                self.playwright.stop()
            self.log("Bot selesai!", "OK")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys, io
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 50)
    print("Facebook Auto-Like Bot v8")
    print("=" * 50)
    
    bot = FacebookAutoLike(CONFIG)
    bot.run()