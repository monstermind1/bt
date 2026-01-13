import os
import time
import threading
from datetime import datetime
from instagrapi import Client
from flask import Flask

exec(open("config.py").read())
exec(open("commands.py").read())

app = Flask(__name__)
STATS = {"total": 0}
known_members = {}
client = None
last_message_ids = {}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def token_login():
    global client
    client = Client()
    try:
        client.login_by_sessionid(SESSION_TOKEN)
        client.dump_settings("session.json")
        log("✅ TOKEN LOGIN SUCCESS!")
        return True
    except Exception as e:
        log(f"💥 LOGIN ERROR: {str(e)[:50]}")
        return False

def process_message(gid, msg):
    """Process single message for commands"""
    if not msg or not msg.text:
        return
    
    text = msg.text.strip().lower()
    sender = None
    
    try:
        thread = client.direct_thread(gid)
        sender = next((u for u in thread.users if u.pk == msg.user_id), None)
    except:
        return
    
    if not sender or sender.username == client.user_id:
        return
    
    sender_name = sender.username
    
    log(f"📨 New msg from @{sender_name}: {text[:30]}")
    
    # AUTO REPLIES
    for keyword, reply in AUTO_REPLIES.items():
        if keyword in text:
            try:
                client.direct_send(reply, [gid])
                log(f"🤖 Auto-reply to @{sender_name}")
                return
            except:
                pass
    
    # COMMANDS
    for cmd, response in COMMANDS.items():
        if text.startswith(cmd):
            try:
                if cmd == "/stats":
                    client.direct_send(f"📊 Total welcomes: {STATS['total']}", [gid])
                else:
                    client.direct_send(response, [gid])
                log(f"✅ @{sender_name} → {cmd}")
                return
            except Exception as e:
                log(f"⚠️ Command failed: {str(e)[:30]}")

def message_monitor():
    """Monitor messages every 5 seconds"""
    global last_message_ids
    
    while client:
        try:
            for gid in GROUP_IDS:
                if gid not in last_message_ids:
                    last_message_ids[gid] = 0
                
                thread = client.direct_thread(gid)
                messages = thread.messages[:10]  # Last 10 messages
                
                for msg in messages:
                    if msg.id > last_message_ids[gid]:
                        process_message(gid, msg)
                        last_message_ids[gid] = max(last_message_ids[gid], msg.id)
            
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            log(f"⚠️ Monitor error: {str(e)[:40]}")
            time.sleep(10)

def member_monitor():
    """Monitor new members"""
    global known_members
    
    while client:
        try:
            for gid in GROUP_IDS:
                if gid not in known_members:
                    known_members[gid] = set()
                
                thread = client.direct_thread(gid)
                current_members = {u.pk for u in thread.users}
                new_members = current_members - known_members[gid]
                
                for user in thread.users:
                    if (user.pk in new_members and user.username):
                        log(f"👋 NEW: @{user.username}")
                        STATS["total"] += 1
                        
                        for msgt in WELCOME_MSGS:
                            welcome = msgt.replace("@user", f"@{user.username}")
                            try:
                                client.direct_send(welcome, [gid])
                                time.sleep(DELAY)
                            except:
                                break
                        
                        known_members[gid] = current_members
                        break
                
                known_members[gid] = current_members
            
            time.sleep(POLL)
            
        except Exception as e:
            log(f"⚠️ Member error: {str(e)[:40]}")
            time.sleep(10)

def start_services():
    """Start both monitoring services"""
    if token_login():
        # Message monitoring
        threading.Thread(target=message_monitor, daemon=True).start()
        log("✅ Message monitor ACTIVE")
        
        # Member monitoring  
        threading.Thread(target=member_monitor, daemon=True).start()
        log("✅ Member monitor ACTIVE")
        
        log("🎉 BOT FULLY OPERATIONAL!")
        return True
    return False

@app.route('/')
def home():
    return f"🤖 NEON BOT LIVE!<br>Total: {STATS['total']}<br>Groups: {len(GROUP_IDS)}"

@app.route('/ping')
def ping():
    return "✅ Bot Active - Commands Working!"

@app.route('/debug')
def debug():
    return f"Client: {client is not None}<br>Groups: {GROUP_IDS}<br>Last IDs: {len(last_message_ids)}"

if __name__ == "__main__":
    start_services()
    port = int(os.environ.get('PORT', 10000))
    log(f"🌐 Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
