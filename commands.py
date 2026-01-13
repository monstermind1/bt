COMMANDS = {
    "/help": "🔥 /ping /stats /music /funny /masti /welcome /token",
    "/ping": "✅ Bot 100% LIVE! 🔥",
    "/stats": "📊 Stats loading...", 
    "/music": "🎵🎶🎤 Music ON! 🎧",
    "/funny": "😂😂😂 Hahaha mast!",
    "/masti": "🎉🥳 Party time bhai!",
    "/welcome": "Test welcome 👋✨",
    "/token": "🔑 Token login active!"
}

AUTO_REPLIES = {
    "hi": "Hey bro! Kya haal? 😎",
    "hello": "Namaste! Welcome! 🔥",
    "kya": "Sab theek bhai! 😄",
    "good": "Good ji! Mast! 👍"
}

def is_admin(username, admin_list):
    return username.lower() in [a.lower() for a in admin_list]
