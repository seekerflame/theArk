import urllib.request
import urllib.parse
import http.cookiejar
import json
import os
import sys
import re
import time
from datetime import datetime

# Configuration
WIKI_API = "https://wiki.opensourceecology.org/api.php"
CREDENTIALS_FILE = ".wiki_credentials"
LEDGER_FILE = "village_ledger_py.json" # Use the active python ledger
STATUS_FILE = "web/wiki_status.json"   # Write into web dir

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def login_and_get_api(username, password, api_call):
    # Login
    log(f"🔑 Logging in as {username}...")
    r = api_call({"action": "query", "meta": "tokens", "type": "login", "format": "json"})
    # Check if login_token exists
    if 'query' not in r or 'tokens' not in r['query']:
        log(f"❌ Failed to get login token. Response: {r}")
        sys.exit(1)
        
    login_token = r['query']['tokens']['logintoken']

    r = api_call({
        "action": "login",
        "lgname": username,
        "lgpassword": password,
        "lgtoken": login_token,
        "format": "json"
    })
    
    if r.get('login', {}).get('result') != "Success":
        log(f"❌ Login failed: {r}")
        write_status("Login Failed", "ERROR")
        sys.exit(1)
        
    return api_call

def write_status(msg, code="SYNCED"):
    try:
        data = {
            "status": code,
            "message": msg,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "last_sync": datetime.now().strftime('%H:%M:%S')
        }
        # Ensure directory exists
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def md_to_wiki(text):
    if not text: return ""
    
    # Headers
    text = re.sub(r'^# (.*?)$', r'= \1 =', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'== \1 ==', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.*?)$', r'=== \1 ===', text, flags=re.MULTILINE)
    
    # Bold/Italic
    text = re.sub(r'\*\*(.*?)\*\*', r"'''\1'''", text)
    text = re.sub(r'\*(.*?)\*', r"''\1''", text)
    
    # Lists
    text = re.sub(r'^\s*-\s', r'* ', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s', r'# ', text, flags=re.MULTILINE)
    
    # Links [Text](URL) -> [URL Text]
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'[\2 \1]', text)
    
    # Code
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    
    return text

def read_file(path):
    # Try local AND parent locations (since we moved to THE_ARK_v0.7)
    candidates = [
        path, 
        f"../{path}",
        f"../../01_Governance/{path}", 
        f"../../{path}",
        f"../../02_Economics/{path}", 
        f"../../03_Technology/{path}",
        f"../../04_Roadmap/{path}",
        f"../../05_Psychology/{path}",
        f"../../06_Operations/Gaia_Protocols/{path}",
        # Fallbacks for older structure if needed
        f"../01_Governance/{path}", 
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    content = f.read().strip()
                    if content: return md_to_wiki(content)
            except:
                pass
    return None # Return None instead of placeholder to allow skipping

def load_credentials():
    if not os.path.exists(CREDENTIALS_FILE):
        log("❌ Credentials file not found.")
        write_status("Missing Credentials", "ERROR")
        sys.exit(1)
    
    with open(CREDENTIALS_FILE, 'r') as f:
        content = f.read()
    
    user = None
    password = None
    for line in content.splitlines():
        if 'WIKI_USER=' in line:
            user = line.split('=')[1].strip('"\'')
        if 'WIKI_PASS=' in line:
            password = line.split('=')[1].strip('"\'')
            
    return user, password

def get_ledger_stats():
    # Try API First
    try:
        with urllib.request.urlopen("http://localhost:3000/api/graph", timeout=2) as url:
            data = json.loads(url.read().decode())
            return len(data), json.dumps(data, indent=2)
    except:
        # Fallback to local file
        log("⚠️ API Offline, reading local ledger...")
        try:
            if os.path.exists(LEDGER_FILE):
                with open(LEDGER_FILE, 'r') as f:
                    data = json.load(f)
                    return len(data), json.dumps(data, indent=2)
        except:
            pass
    return 0, "[]"

    return 0, "[]"

SYNC_ASSETS_DIR = "../../03_Technology/Assets"

def download_file(filename, url):
    target_dir = os.path.join(SYNC_ASSETS_DIR, "Wiki_Downloads")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    target_path = os.path.join(target_dir, filename)
    
    # Skip if exists (simple caching)
    if os.path.exists(target_path):
        return target_path

    try:
        log(f"⬇️ Downloading asset: {filename}...")
        urllib.request.urlretrieve(url, target_path)
        return target_path
    except Exception as e:
        log(f"❌ Failed to download {filename}: {e}")
        return None

def sync_build_files(pages, api_call_func):
    log("🏗️ Checking for Build Files (CAD/STL)...")
    build_files = []
    
    for page in pages:
        # Regex to find [[Media:file.stl]] or [[File:file.fcstd]]
        # Matches: [[(Media|File):(filename.ext)|...]]
        matches = re.findall(r'\[\[(?:Media|File):(.*?)(\|.*?)?\]\]', page['content'], re.IGNORECASE)
        
        for match in matches:
            filename = match[0].strip()
            if filename.lower().endswith(('.stl', '.fcstd', '.step', '.obj')):
                # Get URL
                r = api_call_func({
                    "action": "query",
                    "titles": f"File:{filename}",
                    "prop": "imageinfo",
                    "iiprop": "url",
                    "format": "json"
                })
                
                try:
                    pages_data = r['query']['pages']
                    for pid in pages_data:
                        if 'imageinfo' in pages_data[pid]:
                            url = pages_data[pid]['imageinfo'][0]['url']
                            local_path = download_file(filename, url)
                            if local_path:
                                build_files.append(filename)
                except Exception as e:
                    log(f"⚠️ Error resolving {filename}: {e}")

    if build_files:
        log(f"✅ Synced {len(build_files)} Build Assets")
        return build_files
    return []

def report_audit_to_ledger(pages, summary):
    log("📝 Reporting Audit to Gaia Ledger...")
    try:
        data = json.dumps({
            "pages": pages,
            "summary": summary
        }).encode('utf-8')
        
        req = urllib.request.Request("http://localhost:3000/api/wiki-sync", data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
             res = json.loads(response.read().decode())
             log(f"✅ Gaia Audit Logged: {res.get('tx_hash')}")
    except Exception as e:
        log(f"❌ Failed to report to ledger: {e}")

    return None # Login not needed here

def crawl_wiki(api_call_func):
    log("🕸️ Starting Evolution: Crawling Entire Wiki...")
    
    archive_dir = "library/wiki_archive"
    os.makedirs(archive_dir, exist_ok=True)
    
    # 1. Get All Pages
    ap_continue = None
    all_pages = []
    
    while True:
        params = {
            "action": "query",
            "list": "allpages",
            "aplimit": "5",
            "format": "json"
        }
        if ap_continue:
            params["apcontinue"] = ap_continue
            
        res = api_call_func(params)
        
        if 'query' in res and 'allpages' in res['query']:
            batch = res['query']['allpages']
            all_pages.extend(batch)
            log(f"📍 Found {len(batch)} pages...")
        
        if 'continue' in res:
            ap_continue = res['continue']['apcontinue']
        else:
            break
            
    log(f"✅ Total Pages Found: {len(all_pages)}")
    
    # 2. Fetch Content (in batches)
    batch_size = 20
    crawled_count = 0
    
    for i in range(0, len(all_pages), batch_size):
        chunk = all_pages[i:i+batch_size]
        titles = "|".join([p['title'] for p in chunk])
        
        res = api_call_func({
            "action": "query",
            "prop": "revisions",
            "rvprop": "content",
            "titles": titles,
            "format": "json"
        })
        
        if 'query' in res and 'pages' in res['query']:
            pages_data = res['query']['pages']
            for pid, pdata in pages_data.items():
                if 'revisions' in pdata:
                    title = pdata['title']
                    content = pdata['revisions'][0]['*']
                    
                    # Sanitize filename
                    safe_title = re.sub(r'[^\w\-_.]', '_', title)
                    with open(f"{archive_dir}/{safe_title}.wiki", "w") as f:
                        f.write(f"Title: {title}\n")
                        f.write(f"Url: https://wiki.opensourceecology.org/wiki/{urllib.parse.quote(title)}\n")
                        f.write("-" * 40 + "\n")
                        f.write(content)
                    
                    crawled_count += 1
        
        # Rate limit
        time.sleep(0.5) 
        if i % 100 == 0:
             log(f"📥 Indexed {crawled_count}/{len(all_pages)} pages...")

    log(f"🎉 Evolution Complete: Indexed {crawled_count} pages to {archive_dir}")
    return crawled_count

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--crawl":
        mode = "CRAWL"
    else:
        mode = "SYNC"

    write_status(f"{mode}ing...", "SYNCING")
    log(f"🚀 Starting GAIA Operation: {mode}")
    
    # --- Robust Auth Block ---
    # Try bot credentials first, fallback to user credentials
    bot_creds = ".bot_credentials"
    user_creds = ".wiki_credentials"
    
    username = None
    password = None
    
    if os.path.exists(bot_creds):
        log("🤖 Using Bot Credentials (GaiaBot)")
        with open(bot_creds, 'r') as f:
            for line in f.read().splitlines():
                if 'WIKI_USER=' in line:
                    username = line.split('=')[1].strip('"\'')
                if 'WIKI_PASS=' in line:
                    password = line.split('=')[1].strip('"\'')
    elif os.path.exists(user_creds):
        log("👤 Using User Credentials (Fallback)")
        with open(user_creds, 'r') as f:
            for line in f.read().splitlines():
                if 'WIKI_USER=' in line:
                    username = line.split('=')[1].strip('"\'')
                if 'WIKI_PASS=' in line:
                    password = line.split('=')[1].strip('"\'')
    
    authenticated_api = None
    
    # Define API Call Helper
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)
    
    def api_call(params):
        data = urllib.parse.urlencode(params).encode('utf-8')
        req = urllib.request.Request(WIKI_API, data=data)
        req.add_header('User-Agent', 'CivilizationNode/1.0')
        with urllib.request.urlopen(req) as f:
            return json.loads(f.read().decode('utf-8'))

    if username and password:
        try:
            login_and_get_api(username, password, api_call)
            authenticated_api = api_call
        except Exception as e:
            log(f"Login Failed: {e}")
    
    if not authenticated_api:
        log("❌ OFFLINE: No credentials or login failed.")
        msg = "Missing .wiki_credentials file"
        write_status(msg, "ERROR")
        sys.exit(1)

    if mode == "CRAWL":
        count = crawl_wiki(authenticated_api)
        report_audit_to_ledger([], f"Evolution: Indexed {count} pages from Wiki")
        sys.exit(0)

    # CSRF (Only needed for Edit)
    r = authenticated_api({"action": "query", "meta": "tokens", "format": "json"})
    csrf_token = r['query']['tokens']['csrftoken']

    # Page Data
    block_count, ledger_content = get_ledger_stats()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    pages = [
        {
            "title": "User:Seeker/Abundance_Token",
            "content": f"""= Abundance Token System =
''Powered by GAIA • Synced: {now}''

== Status ==
* '''Network''': '''TESTNET''' (Simulated Village)
* '''Blocks''': {block_count}

== Documentation Index ==
{{| class="wikitable"
|-
! Section !! Wiki Page
|-
| 📜 '''Constitution''' || [[User:Seeker/Abundance_Token/Constitution]]
|-
| 🌱 '''Values''' || [[User:Seeker/Abundance_Token/Values]]
|-
| 💰 '''Economics''' || [[User:Seeker/Abundance_Token/Economics]]
|-
| 📋 '''SOPs''' || [[User:Seeker/Abundance_Token/SOPs]]
|-
| 📚 '''Guide''' || [[User:Seeker/Abundance_Token/Guide]]
|-
| 📊 '''Ledger''' || [[User:Seeker/Abundance_Token/Ledger]]
|}}

[[Category:Abundance Token]]"""
        },
        {
            "title": "User:Seeker/Abundance_Token/Constitution",
            "content": read_file("Constitution.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Values",
            "content": read_file("Village_Values.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Economics",
            "content": read_file("Labor_Valuation_Design.md") + "\n\n== Price Table ==\n" + read_file("Village_Price_Table.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/SOPs",
            "content": read_file("Master_SOP_Index.md") + "\n\n== Emergency SOPs ==\n" + read_file("Emergency_SOPs.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Protocols/Health_and_Sovereignty",
            "content": read_file("Health_and_Sovereignty_Protocols.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Guide",
            "content": read_file("College_Student_Guide.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Ledger",
            "content": f"""= Live Ledger =
''Synced: {now}''

== Status ==
* Blocks: {block_count}

== Raw Data ==
<pre>
{ledger_content}
</pre>

[[Category:Abundance Token]]"""
        },
        {
            "title": "User:Seeker/Future_Builders_Crash_Course_Operations_Manual",
            "content": read_file("00_Master_Operations_Manual.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "Future_Builder_Crash_Course_Enterprise_Development_Spreadsheet",
            "content": read_file("00_Master_Operations_Manual.md") + "\n\n== Original Spreadsheet ==\nUsing this page for the SOP as requested. See History for original."
        },
        {
            "title": "User:Seeker/Abundance_Token/Psychology",
            "content": read_file("User_Psychology.md") + "\n\n[[Category:Abundance Token]]"
        },
        {
            "title": "User:Seeker/Abundance_Token/Master_Plan",
            "content": read_file("../../Abundance_Token_Full_Export.wiki") or "Pending Import..."
        }
    ]

    # Push
    synced_list = []
    
    for page in pages:
        if not page['content'] or "pending sync" in page['content']:
             log(f"⚠️  Skipping {page['title']} (No content found)")
             continue
             
        log(f"📤 Pushing: {page['title']}...")
        r = authenticated_api({
            "action": "edit",
            "title": page['title'],
            "text": page['content'],
            "summary": "GAIA auto-refinement",
            "token": csrf_token,
            "format": "json"
        })
        synced_list.append(page['title'])

    log("🎉 Sync Complete!")
    write_status(f"Synced {len(pages)} pages", "ONLINE")
    
    # Audit to Ledger
    if len(synced_list) > 0:
        report_audit_to_ledger(synced_list, f"Synced {len(synced_list)} pages to Wiki")

    # Sync Build Files
    # For MVP, we scan the pages we just pushed/prepared (User:Seeker/...)
    # + In future, we would query Category:Build.
    # For now, let's assume 'pages' list contains relevant content or we add a specific fetch.
    sync_build_files(pages, authenticated_api)

if __name__ == "__main__":
    main()
