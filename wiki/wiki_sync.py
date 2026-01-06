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
LEDGER_FILE = "village_ledger_py.json" 
STATUS_FILE = "web/wiki_status.json"

ERROR_LOG = "wiki_error.log"

def log(msg):
    timestamp = datetime.now().strftime('%H:%M:%S')
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg)
    try:
        with open(ERROR_LOG, "a") as f:
            f.write(formatted_msg + "\n")
    except:
        pass

def login_and_get_api(username, password, api_call):
    log(f"🔑 Logging in as {username}...")
    r = api_call({"action": "query", "meta": "tokens", "type": "login", "format": "json"})
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
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(data, f)
    except:
        pass

def md_to_wiki(text):
    if not text: return ""
    
    # Tables Parser (Markdown -> MediaWiki)
    lines = text.split('\n')
    new_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        striped_line = line.strip()
        if striped_line.startswith('|') and striped_line.endswith('|'):
            if not in_table:
                # Potential start of table
                has_separator = False
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if re.match(r'^\|[:\- |]+\|$', next_line):
                        has_separator = True
                
                if has_separator:
                    new_lines.append('{| class="wikitable"')
                    in_table = True
                    cells = [c.strip() for c in striped_line.split('|')[1:-1]]
                    new_lines.append('! ' + ' !! '.join(cells))
                    continue 
                else:
                    new_lines.append(line)
            else:
                if re.match(r'^\|[:\- |]+\|$', striped_line):
                    continue
                new_lines.append('|-')
                cells = [c.strip() for c in striped_line.split('|')[1:-1]]
                new_lines.append('| ' + ' || '.join(cells))
        else:
            if in_table:
                new_lines.append('|}')
                in_table = False
            new_lines.append(line)
            
    if in_table:
        new_lines.append('|}')
        
    text = '\n'.join(new_lines)

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
    
    # Code
    text = re.sub(r'```(.*?)```', r'<pre>\1</pre>', text, flags=re.DOTALL)
    
    # GitHub Alerts/Callouts -> Plain Text (Zero Noise)
    def fix_alerts(m):
        lines = m.group(0).split('\n')
        content_lines = []
        for line in lines:
            if line.startswith('>'):
                cleaned = re.sub(r'^>\s*', '', line)
                cleaned = re.sub(r'\[!.*?\]', '', cleaned).strip()
                if cleaned: content_lines.append(cleaned)
        return '\n'.join(content_lines)
    
    text = re.sub(r'^> \[!(.*?)\](?:\n>.*)*', fix_alerts, text, flags=re.MULTILINE)

    # Links Sanitization (file:/// and Markdown -> MediaWiki)
    def fix_links(m):
        description = m.group(1).strip()
        path = m.group(2).strip()
        
        # Strip protocol if present in path
        clean_path = re.sub(r'^file:///.*?\/(.*?)$', r'\1', path)
        filename = urllib.parse.unquote(os.path.basename(clean_path))
        if filename.endswith(".md"): filename = filename[:-3]
        
        mapping = {
            "ECP_001": "Mitosis",
            "CRP_001_Spore_Protocol": "Spore_Protocol",
            "SDP_001": "Documentation_Protocol",
            "MANIFEST": "Manifest",
            "ONBOARDING_FUNNEL": "Onboarding",
            "TOKENOMICS": "Tokenomics",
            "THE_JOURNEY": "The_Journey"
        }
        wiki_title = mapping.get(filename, filename)
        
        # If the description is a full path or same as path, use a clean label
        if "/" in description or description == path or "file:///" in description:
            label = wiki_title.replace("_", " ")
        else:
            label = description
            
        return f"[[User:Seeker/Abundance_Token/{wiki_title}|{label}]]"

    # Match [Label](Path) - Aggressive!
    text = re.sub(r'\[(.*?)\]\((.*?)\)', fix_links, text)
    
    # Match raw file:/// links
    text = re.sub(r'file:///.*?\/(.*?\.md)', lambda m: f"[[User:Seeker/Abundance_Token/{urllib.parse.unquote(m.group(1)[:-3])}|{urllib.parse.unquote(m.group(1)[:-3]).replace('_', ' ')}]]", text)
    
    # Decontaminate remaining local paths
    text = re.sub(r'file:///Volumes/Extreme%20SSD/Antigrav/OSE/CHRONICLE/.*?\/(.*?\.md)', r'[[\1]]', text)
    
    # Fix triple-bracket artifacts
    while "[[[" in text: text = text.replace("[[[", "[[")
    while "]]]" in text: text = text.replace("]]]", "]]")

    # Emoji Stripper
    text = "".join(c for c in text if ord(c) < 0x10000 and ord(c) != 0xFE0F)
    
    if "[[Category:Abundance Token]]" in text:
        text = text.replace("[[Category:Abundance Token]]", "")
        text = text.strip() + "\n\n[[Category:Abundance Token]]"
    
    return text

def read_file(path):
    candidates = [
        path, f"../{path}", f"../../../../CHRONICLE/{path}", f"../../../../CHRONICLE/SOP/{path}",
        f"../../../../CHRONICLE/SESSION_LOGS/2026-01/{path}", f"../../{path}", f"library/{path}",
        f"../../01_Governance/{path}", f"../../02_Economics/{path}", f"../../03_Technology/{path}"
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                with open(p, 'r') as f:
                    return f.read().strip()
            except:
                pass
    return None

def get_ledger_stats():
    try:
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE, 'r') as f:
                data = json.load(f)
                return len(data), json.dumps(data, indent=2)
    except: pass
    return 0, "[]"

def api_call_helper(params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(WIKI_API, data=data)
    req.add_header('User-Agent', 'CivilizationNode/1.0')
    with urllib.request.urlopen(req) as f:
        return json.loads(f.read().decode('utf-8'))

def main():
    mode = "SYNC"
    if len(sys.argv) > 1:
        if "--pull" in sys.argv: mode = "PULL"

    write_status(f"{mode}ing...", "SYNCING")
    log(f"🚀 Operation: {mode}")
    
    # Credentials
    candidates = [
        ".bot_credentials", "../.bot_credentials", "../../.bot_credentials",
        ".wiki_credentials", "../.wiki_credentials", "../../.wiki_credentials"
    ]
    username, password = None, None
    for c in candidates:
        if os.path.exists(c):
            log(f"🔑 Loading credentials from {c}")
            with open(c, 'r') as f:
                for line in f.read().splitlines():
                    if 'WIKI_USER=' in line: username = line.split('=')[1].strip('"\'')
                    if 'WIKI_PASS=' in line: password = line.split('=')[1].strip('"\'')
            if username and password: break
    
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)
    
    if username and password:
        login_and_get_api(username, password, api_call_helper)
    else:
        log("❌ No credentials.")
        sys.exit(1)

    r = api_call_helper({"action": "query", "meta": "tokens", "format": "json"})
    csrf_token = r['query']['tokens']['csrftoken']

    block_count, _ = get_ledger_stats()
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
<div style="max-width: 600px; margin: 20px 0; font-family: 'Inter', sans-serif;">
{{| class="wikitable" style="width: 100%; border: none; border-collapse: collapse; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"
|- style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;"
! style="padding: 12px; text-align: left;" | SECTION !! style="padding: 12px; text-align: left;" | WIKI PORTAL
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''NAVIGATION''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Navigation|ACCESS ROOT]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''ONBOARDING''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Onboarding|START JOURNEY]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''THE OFFER''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Irresistible_Offer|VIEW CHARTER]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''TOKENOMICS''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Tokenomics|SYSTEM ECONOMY]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''MITOSIS''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Mitosis|SCALING LOGIC]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''ROADMAP''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/The_Journey|TIMELINE]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''THE GUIDE''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Guide|KNOWLEDGE BASE]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''HISTORY''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/History|RECORDED OPS]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''MANIFEST''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/Manifest|TERRITORY MAP]]
|-
| style="padding: 12px; border-bottom: 1px solid #eee;" | '''SOPs''' || style="padding: 12px; border-bottom: 1px solid #eee;" | [[User:Seeker/Abundance_Token/SOPs|OPERATIONAL LOGIC]]
|}}
</div>

[[Category:Abundance Token]]"""
        },
        {"title": "User talk:Seeker", "content": read_file("CONSTITUTION.md")},
        {"title": "User:Seeker/Abundance_Token/Navigation", "content": read_file("MASTER_NAVIGATION.md")},
        {"title": "User:Seeker/Abundance_Token/Onboarding", "content": read_file("ONBOARDING_FUNNEL.md")},
        {"title": "User:Seeker/Abundance_Token/Arrival", "content": "#REDIRECT [[User:Seeker/Abundance_Token/Onboarding]]"},
        {"title": "User:Seeker/Abundance_Token/Irresistible_Offer", "content": read_file("IRRESISTIBLE_OFFER_V1.md")},
        {"title": "User:Seeker/Abundance_Token/The_Journey", "content": read_file("THE_JOURNEY.md")},
        {"title": "User:Seeker/Abundance_Token/Guide", "content": read_file("../../03_Technology/College_Student_Guide.md")},
        {"title": "User:Seeker/Abundance_Token/History", "content": read_file("05_CHRONICLE_HISTORY.md")},
        {"title": "User:Seeker/Abundance_Token/Manifest", "content": read_file("MANIFEST.md")},
        {"title": "User:Seeker/Abundance_Token/Charter", "content": "#REDIRECT [[User:Seeker/Abundance_Token/Manifest]]"},
        {"title": "User:Seeker/Abundance_Token/SOPs", "content": read_file("Master_SOP_Index.md")},
        {"title": "User:Seeker/Abundance_Token/Tokenomics", "content": read_file("TOKENOMICS.md")},
        {"title": "User:Seeker/Abundance_Token/Mitosis", "content": read_file("ECP_001.md")},
        {"title": "Dunbar Mitosis", "content": "#REDIRECT [[User:Seeker/Abundance_Token/Mitosis]]"}
    ]

    for page in pages:
        content = page['content']
        if not content: continue
        
        # Add Category
        if "#REDIRECT" not in content and "[[Category:Abundance Token]]" not in content:
            content += "\n\n[[Category:Abundance Token]]"

        log(f"📤 Pushing: {page['title']}...")
        api_call_helper({
            "action": "edit", "title": page['title'], "text": md_to_wiki(content),
            "summary": "GAIA high-fidelity sync (Decontaminated Links + Zero Noise)",
            "token": csrf_token, "format": "json"
        })

    log("🎉 Sync Complete!")
    write_status("Online", "ONLINE")

if __name__ == "__main__":
    main()
