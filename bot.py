import os
import threading
import time
import random
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from instagrapi import Client

exec(open("config.py").read())

app = Flask(__name__)
BOT_THREAD = None
STOP_EVENT = threading.Event()
LOGS = []
SESSION_FILE = "session.json"
STATS = {"total_welcomed": 0, "today_welcomed": 0, "last_reset": datetime.now().date()}

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    lm = "[" + ts + "] " + msg
    LOGS.append(lm)
    print(lm)

MUSIC_EMOJIS = ["🎵", "🎶", "🎸", "🎹", "🎤", "🎧", "🎺", "🎷"]
FUNNY = ["Hahaha! 😂", "LOL! 🤣", "Mast! 😆", "Pagal! 🤪", "King! 👑😂"]
MASTI = ["Party! 🎉", "Masti! 🥳", "Dhamaal! 💃", "Full ON! 🔥", "Enjoy! 🎊"]

def token_login():
    """Token se login"""
    cl = Client()
    try:
        cl.login_by_sessionid(SESSION_TOKEN)
        cl.dump_settings(SESSION_FILE)
        log("✅ TOKEN LOGIN SUCCESS!")
        return cl
    except Exception as e:
        log("💥 TOKEN LOGIN FAILED: " + str(e))
        return None

def run_bot():
    """Main bot logic - tera working code same!"""
    global STATS
    cl = token_login()
    if not cl:
        return
    
    log("🤖 Bot started!")
    log("Admins: " + str(ADMIN_USERS))
    
    km = {}  # known members
    lm = {}  # last message
    
    # Initialize groups
    for gid in GROUP_IDS:
        try:
            g = cl.direct_thread(gid)
            km[gid] = {u.pk for u in g.users}
            lm[gid] = g.messages[0].id if g.messages else None
            log("✅ Group " + gid[:8] + "... ready (" + str(len(g.users)) + " members)")
        except Exception as e:
            log("⚠️ Group error: " + str(e))
            km[gid] = set()
            lm[gid] = None
    
    # Daily reset
    if STATS["last_reset"] != datetime.now().date():
        STATS["today_welcomed"] = 0
        STATS["last_reset"] = datetime.now().date()
    
    while not STOP_EVENT.is_set():
        try:
            for gid in GROUP_IDS:
                if STOP_EVENT.is_set():
                    break
                
                try:
                    g = cl.direct_thread(gid)
                    
                    # MESSAGE PROCESSING (TERA WORKING LOGIC!)
                    if lm[gid]:
                        nm = []
                        for m in g.messages:
                            if m.id == lm[gid]:
                                break
                            nm.append(m)
                        
                        for m in reversed(nm):
                            if m.user_id == cl.user_id:
                                continue
                            
                            sender = next((u for u in g.users if u.pk == m.user_id), None)
                            if not sender:
                                continue
                            
                            su = sender.username.lower()
                            ia = su in [a.lower() for a in ADMIN_USERS] if ADMIN_USERS else True
                            t = m.text.strip() if m.text else ""
                            tl = t.lower()
                            
                            # COMMANDS (TERA SAME CODE!)
                            if tl in ["/help", "!help"]:
                                cl.direct_send("🔥 COMMANDS: /ping /stats /music /funny /masti /count /time /welcome", thread_ids=[gid])
                                log("📱 @" + sender.username + " used /help")
                            
                            elif tl in ["/stats", "!stats"]:
                                cl.direct_send("📊 STATS - Total: " + str(STATS['total_welcomed']) + " | Today: " + str(STATS['today_welcomed']), thread_ids=[gid])
                            
                            elif tl in ["/ping", "!ping"]:
                                cl.direct_send("✅ PONG! Bot 100% ALIVE! 🔥", thread_ids=[gid])
                            
                            elif tl in ["/count", "!count"]:
                                cl.direct_send("👥 MEMBERS: " + str(len(g.users)), thread_ids=[gid])
                            
                            elif tl in ["/music", "!music"]:
                                cl.direct_send("🎵 " + " ".join(random.choices(MUSIC_EMOJIS, k=5)), thread_ids=[gid])
                            
                            elif tl in ["/funny", "!funny"]:
                                cl.direct_send(random.choice(FUNNY), thread_ids=[gid])
                            
                            elif tl in ["/masti", "!masti"]:
                                cl.direct_send(random.choice(MASTI), thread_ids=[gid])
                            
                            elif tl in ["/time", "!time"]:
                                cl.direct_send("🕐 TIME: " + datetime.now().strftime("%I:%M %p"), thread_ids=[gid])
                    
                    # NEW MEMBERS (TERA WORKING LOGIC!)
                    if g.messages:
                        lm[gid] = g.messages[0].id
                    
                    cm = {u.pk for u in g.users}
                    nwm = cm - km[gid]
                    
                    if nwm:
                        for u in g.users:
                            if u.pk in nwm and u.username:
                                log("👋 NEW: @" + u.username)
                                for ms in WELCOME_MSGS:
                                    fm = ("@" + u.username + " " + ms) if True else ms
                                    cl.direct_send(fm, thread_ids=[gid])
                                    STATS["total_welcomed"] += 1
                                    STATS["today_welcomed"] += 1
                                    log("✅ Welcomed @" + u.username)
                                    time.sleep(DELAY)
                                km[gid] = cm
                                break
                    
                    km[gid] = cm
                    
                except Exception as e:
                    log("⚠️ Loop error: " + str(e)[:50])
            
            time.sleep(POLL)
            
        except Exception as e:
            log("💥 Main loop error: " + str(e)[:50])
    
    log("🛑 Bot stopped")

@app.route("/")
def index():
    return f"""
    🤖 NEON BOT LIVE! Total Welcomes: {STATS['total_welcomed']}
    <br><br>
    ✅ Token login: OK
    ✅ Groups: {len(GROUP_IDS)}
    ✅ Commands: /help /ping /stats /music etc
    <br><br>
    <a href="/logs">View Logs</a> | <a href="/stats">Stats</a>
    """

@app.route("/logs")
def get_logs():
    return jsonify({"logs": LOGS[-50:]})

@app.route("/stats")
def get_stats():
    return jsonify(STATS)

@app.route("/start", methods=["POST"])
def start_bot():
    global BOT_THREAD, STOP_EVENT
    if BOT_THREAD and BOT_THREAD.is_alive():
        return jsonify({"status": "already_running"})
    
    STOP_EVENT.clear()
    BOT_THREAD = threading.Thread(target=run_bot, daemon=True)
    BOT_THREAD.start()
    log("🚀 Bot started by web!")
    return jsonify({"status": "started", "message": "Bot running!"})

@app.route("/stop", methods=["POST"])
def stop_bot():
    STOP_EVENT.set()
    log("🛑 Bot stopped by web!")
    return jsonify({"status": "stopped"})

if __name__ == "__main__":
    log("🌐 Web server starting...")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
