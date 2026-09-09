"""
Export Cookies Facebook per Akun
=================================
Jalankan script ini untuk login manual dan simpan cookies ke file JSON.

Cara pakai:
  python export_cookies.py

Browser terbuka otomatis -> login manual di browser ->
cookies tersimpan otomatis setelah login terdeteksi berhasil.
"""

from playwright.sync_api import sync_playwright
import json
import os
import platform
import time
from datetime import datetime

# ═══════════════════════════════════════════════════════
# KONFIGURASI
# ═══════════════════════════════════════════════════════

ACCOUNTS = [
    {
        "label":        "Akun 1 - faturikhsanudin@gmail.com",
        "profile_dir":  "./fb_profile_1",
        "cookies_file": "./cookies/akun1/cookies.json",
    },
    {
        "label":        "Akun 2 - usertestpkl@gmail.com",
        "profile_dir":  "./fb_profile_2",
        "cookies_file": "./cookies/akun2/cookies.json",
    },
    {
        "label":        "Akun 3 - rid7@gmail.com",
        "profile_dir":  "./fb_profile_3",
        "cookies_file": "./cookies/akun3/cookies.json",
    },
    {
        "label":        "Akun 4 - liviny932@gmail.com",
        "profile_dir":  "./fb_profile_4",
        "cookies_file": "./cookies/akun4/cookies.json",
    },
    {
        "label":        "Akun 5 - hindiabelandajepang@gmail.com",
        "profile_dir":  "./fb_profile_5",
        "cookies_file": "./cookies/akun5/cookies.json",
    },
]

CHROME_EXE       = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_PROFILE   = "Profile 20"
CHROME_USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")

# Batas tunggu login manual (detik)
LOGIN_TIMEOUT = 300

# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════

def detect_chrome():
    if os.path.exists(CHROME_EXE):
        return CHROME_EXE
    sys_name = platform.system()
    paths = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
        "Darwin":  ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"],
        "Linux":   ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium"],
    }
    for path in paths.get(sys_name, []):
        if os.path.exists(path):
            return path
    raise Exception("Chrome tidak ditemukan!")


def export_cookies_for(account: dict):
    label        = account["label"]
    profile_dir  = account["profile_dir"]
    cookies_file = account["cookies_file"]

    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"  Output: {cookies_file}")
    print(f"{'='*55}")
    print("[i] Browser terbuka. Login Facebook secara manual.")
    print(f"[i] Bot tunggu otomatis sampai {LOGIN_TIMEOUT} detik.")
    print()

    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(os.path.dirname(cookies_file), exist_ok=True)

    chrome = detect_chrome()

    with sync_playwright() as pw:
        context = pw.chromium.launch_persistent_context(
            user_data_dir=CHROME_USER_DATA,
            executable_path=chrome,
            headless=False,
            args=[
                f"--profile-directory={CHROME_PROFILE}",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--window-size=1366,768",
            ],
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
        )
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
        """)

        # Buka halaman login
        page.goto("https://www.facebook.com/login/")
        print("[i] Halaman login terbuka. Silakan login...")

        # Tunggu otomatis sampai URL bukan login lagi
        try:
            page.wait_for_url(
                lambda url: (
                    "login" not in url
                    and "two_step_verification" not in url
                    and "checkpoint" not in url
                    and "facebook.com" in url
                ),
                timeout=LOGIN_TIMEOUT * 1000,
            )
            print("[+] Login terdeteksi!")
        except Exception:
            # Cek manual sekali lagi
            curr = page.url
            if "login" in curr or "facebook.com" not in curr:
                print("[x] Timeout atau login gagal.")
                context.close()
                return

        # Tunggu sebentar biar cookies session terbentuk
        time.sleep(3)

        # Ambil semua cookies Facebook
        cookies = context.cookies()
        fb_cookies = [
            c for c in cookies
            if "facebook.com" in c.get("domain", "")
        ]

        # Simpan
        with open(cookies_file, "w", encoding="utf-8") as f:
            json.dump(fb_cookies, f, indent=2, ensure_ascii=False)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[+] {len(fb_cookies)} cookies disimpan ke: {cookies_file}")
        print(f"[i] Waktu export: {ts}")

        context.close()


# ═══════════════════════════════════════════════════════
# MAIN — tanpa wrap stdout agar input() tidak stuck
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("  Facebook Cookie Exporter")
    print("=" * 55)
    print()

    # Tampilkan status tiap akun
    for i, acc in enumerate(ACCOUNTS, 1):
        status = "[ADA]   " if os.path.exists(acc["cookies_file"]) else "[BELUM] "
        print(f"  {i}. {status} {acc['label']}")

    print()
    print("Pilihan:")
    print("  0 = Export semua akun")
    print("  1-5 = Export 1 akun")
    print()

    try:
        pilihan = input("Masukkan pilihan: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nDibatalkan.")
        exit(0)

    if pilihan == "0":
        for i, account in enumerate(ACCOUNTS, 1):
            print(f"\n[{i}/{len(ACCOUNTS)}] {account['label']}")
            try:
                lanjut = input("Export akun ini? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nDibatalkan.")
                break
            if lanjut == "n":
                print("Dilewati.")
                continue
            export_cookies_for(account)
        print("\n[+] Selesai! Semua cookies tersimpan.")
        print("[i] Sekarang jalankan: python auto_like.py")

    elif pilihan.isdigit() and 1 <= int(pilihan) <= len(ACCOUNTS):
        idx = int(pilihan) - 1
        export_cookies_for(ACCOUNTS[idx])
        print("\n[+] Selesai!")
        print("[i] Sekarang jalankan: python auto_like.py")

    else:
        print("[x] Pilihan tidak valid.")
