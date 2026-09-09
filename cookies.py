"""
Script untuk input cookies Facebook manual
- User input email, password, dan cookies
- Simpan ke file JSON untuk digunakan bot
"""

from playwright.sync_api import sync_playwright
import json
import os
import time
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════
# KONFIGURASI
# ═══════════════════════════════════════════════════════

CONFIG = {
    # Folder untuk menyimpan cookies
    "cookies_dir": "./cookies",
    
    # Folder untuk menyimpan data akun
    "accounts_dir": "./accounts",
}

# ═══════════════════════════════════════════════════════
# ACCOUNT MANAGER
# ═══════════════════════════════════════════════════════

class AccountManager:
    """Manage akun dan cookies"""
    
    def __init__(self, config):
        self.config = config
        self.cookies_dir = Path(config.get("cookies_dir", "./cookies"))
        self.accounts_dir = Path(config.get("accounts_dir", "./accounts"))
        
        # Buat folder jika belum ada
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        
        # File untuk menyimpan data akun
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
        # Cek apakah akun sudah ada
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
    
    def update_account(self, name, email, password):
        """Update akun yang sudah ada"""
        for account in self.accounts:
            if account["name"] == name:
                account["email"] = email
                account["password"] = password
                account["updated_at"] = datetime.now().isoformat()
                self.save_accounts()
                print(f"✅ Akun {name} berhasil diupdate!")
                return account
        
        # Jika tidak ada, tambah baru
        return self.add_account(name, email, password)
    
    def get_account(self, name):
        """Get akun berdasarkan nama"""
        for account in self.accounts:
            if account["name"] == name:
                return account
        return None
    
    def list_accounts(self):
        """List semua akun"""
        return self.accounts
    
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
    
    def __init__(self, config):
        self.config = config
        self.cookies_dir = Path(config.get("cookies_dir", "./cookies"))
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_cookies(self, cookies):
        """Validasi cookies Facebook"""
        required_cookies = ["c_user", "xs", "fr", "datr"]
        
        if not isinstance(cookies, list):
            print("❌ Cookies harus berupa list/array")
            return False
        
        cookie_names = [c.get("name") for c in cookies if isinstance(c, dict)]
        
        missing = []
        for required in required_cookies:
            if required not in cookie_names:
                missing.append(required)
        
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
    
    def load_cookies(self, account_name):
        """Load cookies dari file"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        if not cookies_file.exists():
            return None
        
        try:
            with open(cookies_file, "r") as f:
                return json.load(f)
        except:
            return None
    
    def delete_cookies(self, account_name):
        """Hapus cookies file"""
        cookies_file = self.cookies_dir / f"{account_name}_cookies.json"
        
        if cookies_file.exists():
            cookies_file.unlink()
            print(f"✅ Cookies untuk {account_name} dihapus!")
            return True
        return False

# ═══════════════════════════════════════════════════════
# INPUT HANDLER
# ═══════════════════════════════════════════════════════

class InputHandler:
    """Handle input dari user"""
    
    def __init__(self, config):
        self.config = config
        self.account_manager = AccountManager(config)
        self.cookies_manager = CookiesManager(config)
    
    def input_account_and_cookies(self):
        """Input email, password, dan cookies"""
        print(f"\n{'='*50}")
        print("INPUT AKUN & COOKIES")
        print(f"{'='*50}")
        
        # Tampilkan akun yang sudah ada
        accounts = self.account_manager.list_accounts()
        if accounts:
            print("\nAkun yang sudah terdaftar:")
            for i, account in enumerate(accounts, 1):
                has_cookies = "✅" if self.cookies_manager.load_cookies(account["name"]) else "❌"
                print(f"{i}. {account['name']} ({account['email']}) - Cookies: {has_cookies}")
            print()
        
        # Pilih mode
        print("Pilih mode:")
        print("1. Tambah akun baru")
        print("2. Update akun yang sudah ada")
        
        mode = input("\nPilih (1-2): ").strip()
        
        if mode == "1":
            # Tambah akun baru
            print("\n--- Tambah Akun Baru ---")
            
            # Input nama akun
            while True:
                name = input("Nama akun (contoh: account1): ").strip()
                if name:
                    # Cek apakah nama sudah ada
                    if self.account_manager.get_account(name):
                        print(f"⚠️ Nama akun {name} sudah ada!")
                        continue
                    break
                print("❌ Nama akun tidak boleh kosong!")
            
            # Input email
            while True:
                email = input("Email Facebook: ").strip()
                if email and "@" in email:
                    break
                print("❌ Email tidak valid!")
            
            # Input password
            while True:
                password = input("Password Facebook: ").strip()
                if password:
                    break
                print("❌ Password tidak boleh kosong!")
            
            # Simpan akun
            account = self.account_manager.add_account(name, email, password)
            
        elif mode == "2":
            # Update akun yang sudah ada
            if not accounts:
                print("❌ Tidak ada akun yang terdaftar!")
                return False
            
            print("\n--- Update Akun ---")
            
            # Pilih akun
            for i, account in enumerate(accounts, 1):
                print(f"{i}. {account['name']} ({account['email']})")
            
            try:
                idx = int(input("\nPilih nomor akun: ")) - 1
                if idx < 0 or idx >= len(accounts):
                    print("❌ Nomor tidak valid!")
                    return False
            except ValueError:
                print("❌ Input harus angka!")
                return False
            
            account = accounts[idx]
            name = account["name"]
            
            print(f"\nUpdate akun: {name}")
            
            # Update email
            new_email = input(f"Email [{account['email']}]: ").strip()
            email = new_email if new_email else account["email"]
            
            # Update password
            new_password = input("Password (kosongkan jika tidak diubah): ").strip()
            password = new_password if new_password else account["password"]
            
            # Update akun
            account = self.account_manager.update_account(name, email, password)
        
        else:
            print("❌ Mode tidak valid!")
            return False
        
        # Input cookies
        print(f"\n--- Input Cookies untuk {account['name']} ---")
        print("Paste cookies JSON di bawah ini:")
        print("(Copy dari extension Cookie-Editor > Export > JSON)")
        print("(Akhiri dengan baris kosong dan tekan Enter)")
        print()
        
        # Baca input multi-baris
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
        
        # Parse JSON
        try:
            json_text = "\n".join(lines)
            cookies_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            print(f"❌ Format JSON tidak valid: {e}")
            print("Pastikan format JSON benar!")
            return False
        
        # Validasi cookies
        if not self.cookies_manager.validate_cookies(cookies_data):
            print("❌ Cookies tidak valid!")
            return False
        
        # Simpan cookies
        self.cookies_manager.save_cookies(account["name"], cookies_data)
        
        print(f"\n✅ Akun {account['name']} berhasil disimpan!")
        print(f"   Email: {account['email']}")
        print(f"   Cookies: {len(cookies_data)} items")
        
        return True
    
    def list_all_data(self):
        """List semua akun dan cookies"""
        accounts = self.account_manager.list_accounts()
        
        if not accounts:
            print("\n❌ Tidak ada akun yang terdaftar!")
            return
        
        print(f"\n{'='*50}")
        print("DATA AKUN & COOKIES")
        print(f"{'='*50}")
        
        for account in accounts:
            print(f"\n📁 {account['name']}")
            print(f"   Email: {account['email']}")
            
            cookies = self.cookies_manager.load_cookies(account["name"])
            if cookies:
                print(f"   Cookies: ✅ ({len(cookies)} items)")
                
                # Tampilkan info penting
                for cookie in cookies:
                    if cookie.get("name") in ["c_user", "xs", "fr", "datr"]:
                        value = cookie.get("value", "")
                        print(f"   - {cookie['name']}: {value[:30]}...")
            else:
                print(f"   Cookies: ❌ (belum ada)")
    
    def delete_account_data(self):
        """Hapus data akun dan cookies"""
        accounts = self.account_manager.list_accounts()
        
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
    
    # Handle UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    input_handler = InputHandler(CONFIG)
    
    while True:
        print("\n" + "=" * 50)
        print("FACEBOOK COOKIES MANAGER")
        print("=" * 50)
        print("1. Input akun & cookies")
        print("2. List semua data")
        print("3. Hapus data akun")
        print("4. Keluar")
        print("=" * 50)
        
        choice = input("Pilih menu (1-4): ").strip()
        
        if choice == "1":
            input_handler.input_account_and_cookies()
            
        elif choice == "2":
            input_handler.list_all_data()
            
        elif choice == "3":
            input_handler.delete_account_data()
            
        elif choice == "4":
            print("\nSampai jumpa!")
            break
            
        else:
            print("❌ Pilihan tidak valid!")