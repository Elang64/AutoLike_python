"""
Facebook Auto-Like Bot v9 - Complete System
- Input cookies manual (email, password, cookies)
- Auto-like target post menggunakan cookies
- Support multiple accounts
- Semua dalam satu file
- Bisa input postingan target secara manual
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
    # Target URL (akan diisi oleh user)
    "target_url": "",
    
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
    
    # Folder untuk menyimpan data
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
        """Load data akun dari file"""
        if self.accounts_file.exists():
            try:
                with open(self.accounts_file, "r") as f:
                    self.accounts = json.load(f)
            except:
                self.accounts = []
        else:
            self.accounts = []
    
    def save_accounts(self):
        """Simpan data akun ke file"""
        with open(self.accounts_file, "w") as f:
            json.dump(self.accounts, f, indent=2)
    
    def add_account(self, name, email, password):
        """Tambah akun baru"""
        for account in self.accounts:
            if account["email"] == email:
                print(f"⚠️ Akun dengan email {email} sudah ada!")
                return None
        
        account = {
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now().isoformat(),
        }
        
        self.accounts.append(account)
        self.save_accounts()
        print(f"✅ Akun {name} berhasil ditambahkan!")
        return account
    
    def get_account(self, name):
        """Get akun berdasarkan nama"""
        for account in self.accounts:
            if account["name"] == name:
                return account
        return None
    
    def get_all_accounts(self):
        """Get semua akun"""
        return self.accounts
    
    def get_accounts_with_cookies(self, cookies_dir):
        """Get akun yang memiliki cookies"""
        accounts_with_cookies = []
        
        for account in self.accounts:
            cookies_file = Path(cookies_dir) / f"{account['name']}_cookies.json"
            if cookies_file.exists():
                account["cookies_file"] = str(cookies_file)
                accounts_with_cookies.append(account)
        
        return accounts_with_cookies
    
    def delete_account(self, name):
        """Hapus akun"""
        for i, account in enumerate(self.accounts):
            if account["name"] == name:
                del self.accounts[i]
                self.save_accounts()
                print(f"✅ Akun {name} berhasil dihapus!")
                return True
        return False

# ═══════════════════════════════════════════════════════
# COOKIES MANAGER
# ═══════════════════════════════════════════════════════

class CookiesManager:
    """Manage cookies"""
    
    def __init__(self, cookies_dir: str = "./cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_cookies(self, cookies) -> bool:
        """Validasi cookies Facebook"""
        required = ["c_user", "xs", "fr", "datr"]
        
        if not isinstance(cookies, list):
            print("❌ Cookies harus berupa list/array")
            return False
        
        cookie_names = [c.get("name") for c in cookies if isinstance(c, dict)]
        
        missing = [r for r in required if r not in cookie_names]
        
        if missing:
            print(f"⚠️ Cookies wajib tidak ditemukan: {', '.join(missing)}")
            print("Cookies yang ditemukan:")
            for name in cookie_names:
                print(f"  - {name}")
            return False
        
        # Check user ID
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
    
    def save_cookies(self, account_name, cookies):
        """Simpan cookies ke file"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Cookies disimpan ke: {cookies_file}")
        return cookies_file
    
    def load_cookies(self, account_name) -> Optional[List[Dict]]:
        """Load cookies dari file"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        if not cookies_file.exists():
            return None
        
        try:
            with open(cookies_file, "r", encoding="utf-8") as f:
                cookies = json.load(f)
            return cookies
        except:
            return None
    
    def delete_cookies(self, account_name):
        """Hapus cookies"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        if cookies_file.exists():
            cookies_file.unlink()
            print(f"✅ Cookies untuk {account_name} dihapus!")
            return True
        return False
    
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
            return path
    
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
        
        self.context = self.browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        
        self.page = self.context.new_page()
        
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
        
        cookies = self.cookies_manager.load_cookies(account_name)
        
        if not cookies:
            self.log(f"Tidak ada cookies untuk {account_name}", "ERR")
            return
        
        if not self.cookies_manager.validate_cookies(cookies):
            self.log("Cookies tidak valid!", "ERR")
            return
        
        formatted_cookies = self.cookies_manager.format_for_playwright(cookies)
        
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
        
        if not target_url:
            self.log("❌ Target URL belum diisi! Silakan input melalui menu.", "ERR")
            return False
        
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
        # Cek apakah target URL sudah diisi
        if not self.config["target_url"]:
            self.log("❌ Target URL belum diisi! Silakan input melalui menu.", "ERR")
            return
        
        accounts = self.account_manager.get_accounts_with_cookies(self.config["cookies_dir"])
        
        if not accounts:
            self.log("Tidak ada akun dengan cookies!", "ERR")
            self.log("Silakan input cookies dulu melalui menu", "WARN")
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
# INPUT HANDLER
# ═══════════════════════════════════════════════════════

class InputHandler:
    """Handle input dari user"""
    
    def __init__(self, config):
        self.config = config
        self.account_manager = AccountManager(config.get("accounts_dir", "./accounts"))
        self.cookies_manager = CookiesManager(config.get("cookies_dir", "./cookies"))
    
    def input_target_post(self):
        """Input target post URL"""
        print(f"\n{'='*50}")
        print("INPUT TARGET POST")
        print(f"{'='*50}")
        print("Masukkan URL postingan Facebook yang ingin di-like")
        print("Contoh: https://www.facebook.com/share/p/19bZGdqXqQ/")
        print("Atau: https://www.facebook.com/username/posts/123456789")
        print()
        
        current_target = self.config.get("target_url", "")
        if current_target:
            print(f"Target saat ini: {current_target}")
            change = input("Ganti target? (y/n): ").strip().lower()
            if change != "y":
                print("Target tetap sama")
                return
        
        while True:
            url = input("URL postingan: ").strip()
            
            if not url:
                print("❌ URL tidak boleh kosong!")
                continue
            
            # Validasi basic URL Facebook
            if "facebook.com" not in url.lower():
                print("❌ URL harus mengandung 'facebook.com'")
                continue
            
            self.config["target_url"] = url
            print(f"✅ Target post berhasil di-set: {url}")
            break
    
    def input_account_and_cookies(self):
        """Input email, password, dan cookies"""
        print(f"\n{'='*50}")
        print("INPUT AKUN & COOKIES")
        print(f"{'='*50}")
        
        # Tampilkan akun yang ada
        accounts = self.account_manager.get_all_accounts()
        if accounts:
            print("\nAkun yang sudah terdaftar:")
            for i, account in enumerate(accounts, 1):
                has_cookies = "✅" if self.cookies_manager.load_cookies(account["name"]) else "❌"
                print(f"{i}. {account['name']} ({account['email']}) - Cookies: {has_cookies}")
            print()
        
        # Input nama akun
        while True:
            name = input("Nama akun (contoh: account1): ").strip()
            if name:
                existing = self.account_manager.get_account(name)
                if existing:
                    print(f"ℹ️ Akun {name} sudah ada, akan diupdate")
                    email = input(f"Email [{existing['email']}]: ").strip()
                    password = input("Password (kosongkan jika tidak diubah): ").strip()
                    
                    email = email if email else existing["email"]
                    password = password if password else existing["password"]
                    
                    self.account_manager.add_account(name, email, password)
                else:
                    email = input("Email Facebook: ").strip()
                    password = input("Password Facebook: ").strip()
                    
                    if email and password:
                        self.account_manager.add_account(name, email, password)
                    else:
                        print("❌ Email dan password wajib diisi!")
                        continue
                break
            print("❌ Nama akun tidak boleh kosong!")
        
        # Input cookies
        print(f"\n--- Input Cookies untuk {name} ---")
        print("Paste cookies JSON di bawah ini:")
        print("(Copy dari extension Cookie-Editor > Export > JSON)")
        print("(Akhiri dengan baris kosong dan tekan Enter)")
        print()
        
        lines = []
        print("Paste JSON sekarang:")
        
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                lines.append(line)
            except EOFError:
                break
        
        if not lines:
            print("❌ Tidak ada input cookies!")
            return False
        
        try:
            json_text = "\n".join(lines)
            cookies_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"❌ Format JSON tidak valid: {e}")
            return False
        
        if not self.cookies_manager.validate_cookies(cookies_data):
            print("❌ Cookies tidak valid!")
            return False
        
        self.cookies_manager.save_cookies(name, cookies_data)
        
        print(f"\n✅ Akun {name} berhasil disimpan!")
        print(f"   Email: {email}")
        print(f"   Cookies: {len(cookies_data)} items")
        
        return True
    
    def list_all_data(self):
        """List semua akun dan cookies"""
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            print("\n❌ Tidak ada akun yang terdaftar!")
            return
        
        print(f"\n{'='*50}")
        print("DATA AKUN & COOKIES")
        print(f"{'='*50}")
        
        # Tampilkan target URL
        target_url = self.config.get("target_url", "")
        if target_url:
            print(f"\n🎯 Target Post: {target_url}")
        else:
            print(f"\n🎯 Target Post: BELUM DI-SET")
        print()
        
        for account in accounts:
            print(f"\n📁 {account['name']}")
            print(f"   Email: {account['email']}")
            
            cookies = self.cookies_manager.load_cookies(account["name"])
            if cookies:
                print(f"   Cookies: ✅ ({len(cookies)} items)")
                
                for cookie in cookies:
                    if cookie.get("name") in ["c_user", "xs", "fr", "datr"]:
                        value = cookie.get("value", "")
                        print(f"   - {cookie['name']}: {value[:30]}...")
            else:
                print(f"   Cookies: ❌ (belum ada)")
    
    def delete_account_data(self):
        """Hapus data akun dan cookies"""
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            print("\n❌ Tidak ada akun yang terdaftar!")
            return
        
        print(f"\n{'='*50}")
        print("HAPUS DATA AKUN")
        print(f"{'='*50}")
        
        for i, account in enumerate(accounts, 1):
            print(f"{i}. {account['name']} ({account['email']})")
        
        try:
            idx = int(input("\nPilih nomor akun: ")) - 1
            if idx < 0 or idx >= len(accounts):
                print("❌ Nomor tidak valid!")
                return
        except ValueError:
            print("❌ Input harus angka!")
            return
        
        account = accounts[idx]
        name = account["name"]
        
        print(f"\nHapus akun {name}?")
        print("1. Hapus akun saja")
        print("2. Hapus akun dan cookies")
        print("3. Batal")
        
        choice = input("Pilih (1-3): ").strip()
        
        if choice == "1":
            self.account_manager.delete_account(name)
        elif choice == "2":
            self.account_manager.delete_account(name)
            self.cookies_manager.delete_cookies(name)
        else:
            print("Dibatalkan")

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys, io
    
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    input_handler = InputHandler(CONFIG)
    bot = FacebookAutoLike(CONFIG)
    
    while True:
        print("\n" + "=" * 50)
        print("FACEBOOK AUTO-LIKE BOT v9")
        print("=" * 50)
        print("1. Input target postingan")
        print("2. Input akun & cookies")
        print("3. List semua data")
        print("4. Hapus data akun")
        print("5. Jalankan bot (auto-like)")
        print("6. Keluar")
        print("=" * 50)
        
        choice = input("Pilih menu (1-6): ").strip()
        
        if choice == "1":
            input_handler.input_target_post()
            
        elif choice == "2":
            input_handler.input_account_and_cookies()
            
        elif choice == "3":
            input_handler.list_all_data()
            
        elif choice == "4":
            input_handler.delete_account_data()
            
        elif choice == "5":
            bot.run()
            
        elif choice == "6":
            print("\nSampai jumpa!")
            break
            
        else:
            print("❌ Pilihan tidak valid!")