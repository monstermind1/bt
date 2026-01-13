import os
import time
import random
from datetime import datetime
from instagrapi import Client

exec(open("config.py").read())
exec(open("commands.py").read())

STATS = {"total": 0}
known_members = {}
client = None

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    try:
        with open("bot.log", "a") as f:
            f.write(f"[{ts}] {msg}")
    except:
        pass

def token_login():
    global client
    client = Client()
    try:
        client.login_by_sessionid(SESSION_TOKEN)
        client.dump_settings("session.json")
        log("✅ TOKEN LOGIN SUCCESS!")
        return True
    except Exception as e:
        log(f"💥 TOKEN ERROR: {str(e)[:50]}")
        return False

def start():
    log("🚀 🔥 NEON BOT v6.2 - FULL AUTO!")
    
    if not token_login():
        log("💥 TOKEN LOGIN FAILED - Check config.py")
        return False
    
    for gid in GROUP_IDS:
        try:
            t = client.direct_thread(gid)
            known_members[gid] = {u.pk for u in t.users}
            log(f"✅ Group {gid[:8]}... ({len(t.users)} members)")
        except Exception as e:
            log(f"⚠️ Group {gid}: {str(e)[:30]}")
            known_members[gid] = set()
    
    log("🎉 BOT 100% LIVE!")
    log("💡 /help /ping /stats commands ready!")
    return True

def handle_msg(gid, t, msg):
    text = msg.text.strip().lower() if msg.text else ""
    if msg.user_id == client.user_id: return
    
    sender = next((u for u in t.users if u.pk == msg.user_id), None)
    if not sender: return
    
    sender_name = sender.username
    
    # Auto replies
    for k, v in AUTO_REPLIES.items():
        if k in text:
            try:
                client.direct_send(v, [gid])
                log(f"🤖 Auto: @{sender_name}")
            except:
                pass
            return
    
    # Commands
    for cmd in COMMANDS:
        if text.startswith(cmd):
            try:
                if cmd == "/stats":
                    client.direct_send(f"📊 Total welcomes: {STATS['total']}", [gid])
                else:
                    client.direct_send(COMMANDS[cmd], [gid])
                log(f"📱 @{sender_name}: {text}")
            except:
                pass
            return

if __name__ == "__main__":
    if start():
        last_msgs = {}
        log("🔄 Bot loop started - monitoring groups...")
        while True:
            for gid in GROUP_IDS:
                try:
                    t = client.direct_thread(gid)
                    
                    # New messages
                    if last_msgs.get(gid) and t.messages:
                        new_msgs = [m for m in t.messages if m.id != last_msgs[gid]]
                        for msg in reversed(new_msgs):
                            handle_msg(gid, t, msg)
                    
                    last_msgs[gid] = t.messages[0].id if t.messages else None
                    
                    # NEW MEMBERS
                    current_members = {u.pk for u in t.users}
                    new_members = current_members - known_members.get(gid, set())
                    
                    for user in t.users:
                        if (user.pk in new_members and 
                            user.username and 
                            user.username != SESSION_TOKEN.split(':')[0]):
                            
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
                    
                except Exception as e:
                    log(f"⚠️ Loop: {str(e)[:40]}")
            
            time.sleep(POLL)
    else:
        log("💥 START FAILED - Check SESSION_TOKEN")
        while True:
            time.sleep(60)
