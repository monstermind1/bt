COMMANDS = {
    "/help": "🔥 /ping /stats /music /funny /masti /welcome",
    "/ping": "✅ Bot LIVE! 🔥",
    "/stats": "📊 Stats loading...", 
    "/music": "🎵🎶 Music ON! 🎧",
    "/funny": "😂😂 Hahaha mast!",
    "/masti": "🎉🥳 Party time!",
    "/welcome": "Test welcome 👋",
    
    # 👑 ADMIN ONLY COMMANDS
    "/kick": "👢 /kick @username - Admin only",
    "/spam": "💥 /spam @user message - Admin only",
    "/ban": "🚫 /ban @username - Admin only"
}

AUTO_REPLIES = {
    "hi": "Hey bro! 😎",
    "hello": "Namaste! 🔥",
    "kya": "Sab theek! 😄"
}

def is_admin(username, admin_list):
    """Check admin status"""
    return username.lower() in [a.lower() for a in admin_list]
