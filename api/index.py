from flask import Flask, request, jsonify, render_template_string
import os
import json
import time
import hashlib
import secrets
import random
from datetime import datetime
from collections import defaultdict
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ========== IN-MEMORY DATABASE ==========
class HackArenaDB:
    def __init__(self):
        self.users = {}
        self.games = {}
        self.messages = defaultdict(list)
        self.leaderboard = []
        self.online_users = set()
        self.init_default_data()
    
    def init_default_data(self):
        # Default users
        self.users = {
            "admin": {"username": "admin", "points": 1500, "rank": "👑 Elite Hacker", "level": 99},
            "ghost": {"username": "ghost_1337", "points": 800, "rank": "👻 Ghost", "level": 42},
            "crypto": {"username": "crypto_master", "points": 650, "rank": "🔐 Cryptographer", "level": 35},
            "netrunner": {"username": "net_runner", "points": 520, "rank": "🌐 Network Ninja", "level": 28}
        }
        
        # Default leaderboard
        self.leaderboard = [
            {"username": "admin", "points": 1500, "rank": "👑 Elite Hacker"},
            {"username": "ghost_1337", "points": 800, "rank": "👻 Ghost"},
            {"username": "crypto_master", "points": 650, "rank": "🔐 Cryptographer"},
            {"username": "net_runner", "points": 520, "rank": "🌐 Network Ninja"},
            {"username": "binary_bender", "points": 480, "rank": "💾 Binary Breaker"},
            {"username": "script_kiddie", "points": 350, "rank": "📟 Script Kiddie"},
            {"username": "dark_matter", "points": 280, "rank": "⚫ Dark Matter"},
            {"username": "zero_cool", "points": 220, "rank": "❄️ Zero Cool"},
            {"username": "acid_burn", "points": 180, "rank": "🔥 Acid Burn"},
            {"username": "crash_override", "points": 150, "rank": "💥 Crash Override"}
        ]
        
        # Default games
        self.games = {
            "password_cracker": {
                "name": "🔐 Password Cracker",
                "description": "Crack MD5 hashes to find passwords",
                "difficulty": "Easy",
                "points": 50
            },
            "network_scanner": {
                "name": "🌐 Network Scanner",
                "description": "Scan networks and find open ports",
                "difficulty": "Medium",
                "points": 100
            },
            "cryptography": {
                "name": "🔏 Cryptography",
                "description": "Decrypt encoded messages",
                "difficulty": "Hard",
                "points": 150
            },
            "binary_exploit": {
                "name": "💾 Binary Exploit",
                "description": "Find and exploit buffer overflows",
                "difficulty": "Expert",
                "points": 200
            },
            "ctf": {
                "name": "🏴 CTF Challenge",
                "description": "Capture The Flag - Multi-level challenge",
                "difficulty": "Insane",
                "points": 500
            }
        }

db = HackArenaDB()

# ========== HTML TEMPLATES ==========
MAIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 HACKARENA - Ultimate Hacking Playground</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            overflow-x: hidden;
            min-height: 100vh;
        }
        .matrix-bg {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: -1;
            opacity: 0.1;
        }
        .header {
            background: rgba(0, 0, 0, 0.95);
            border-bottom: 3px solid #00ff00;
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 0 40px rgba(0, 255, 0, 0.4);
        }
        .logo {
            font-size: 2.5rem;
            font-weight: bold;
            background: linear-gradient(45deg, #ff0000, #00ff00, #0000ff, #ff00ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            animation: glitch 3s infinite;
        }
        @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0); }
        }
        .nav a {
            color: #00ff00;
            text-decoration: none;
            margin: 0 15px;
            padding: 10px 20px;
            border: 2px solid transparent;
            transition: all 0.3s;
            font-size: 1.1rem;
        }
        .nav a:hover {
            border-color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            background: rgba(0, 255, 0, 0.1);
        }
        .hero {
            text-align: center;
            padding: 100px 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .hero h1 {
            font-size: 4.5rem;
            margin-bottom: 30px;
            text-shadow: 0 0 30px #00ff00;
            color: #00ffff;
        }
        .hero p {
            font-size: 1.5rem;
            margin-bottom: 50px;
            color: #88ff88;
        }
        .btn {
            display: inline-block;
            padding: 18px 36px;
            margin: 15px;
            font-size: 1.3rem;
            background: transparent;
            color: #00ff00;
            border: 3px solid;
            text-decoration: none;
            transition: all 0.3s;
            cursor: pointer;
            font-family: inherit;
        }
        .btn:hover {
            background: #00ff00;
            color: #000;
            box-shadow: 0 0 40px #00ff00;
            transform: translateY(-5px);
        }
        .btn-primary { border-color: #00ff00; }
        .btn-danger { border-color: #ff0000; color: #ff0000; }
        .btn-danger:hover { background: #ff0000; color: #000; box-shadow: 0 0 40px #ff0000; }
        .btn-cyan { border-color: #00ffff; color: #00ffff; }
        .btn-cyan:hover { background: #00ffff; color: #000; box-shadow: 0 0 40px #00ffff; }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            padding: 60px 40px;
            max-width: 1400px;
            margin: 0 auto;
        }
        .feature-card {
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid;
            border-radius: 15px;
            padding: 30px;
            transition: all 0.3s;
            cursor: pointer;
        }
        .feature-card:hover {
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0, 255, 0, 0.3);
        }
        .feature-card h3 {
            font-size: 1.8rem;
            margin-bottom: 20px;
        }
        .card-games { border-color: #ff00ff; }
        .card-terminal { border-color: #00ffff; }
        .card-chat { border-color: #ffff00; }
        .card-leaderboard { border-color: #ff0000; }
        
        .leaderboard {
            padding: 60px 40px;
            max-width: 1000px;
            margin: 0 auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            border: 2px solid #00ff00;
        }
        th, td {
            padding: 20px;
            border: 1px solid #00ff00;
            text-align: left;
        }
        th {
            background: rgba(0, 255, 0, 0.2);
            font-size: 1.2rem;
        }
        tr:hover {
            background: rgba(0, 255, 0, 0.1);
        }
        
        .stats {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.9);
            padding: 15px 25px;
            border: 2px solid #00ff00;
            border-radius: 10px;
            font-size: 0.9rem;
        }
        
        .scan-line {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff00, transparent);
            box-shadow: 0 0 20px #00ff00;
            animation: scan 3s linear infinite;
            z-index: 1000;
        }
        @keyframes scan {
            0% { top: 0; }
            100% { top: 100%; }
        }
    </style>
</head>
<body>
    <canvas class="matrix-bg" id="matrixCanvas"></canvas>
    <div class="scan-line"></div>
    
    <div class="header">
        <div class="logo">HACKARENA</div>
        <div class="nav">
            <a href="/">🏠 HOME</a>
            <a href="/games">🎮 GAMES</a>
            <a href="/terminal">💻 TERMINAL</a>
            <a href="/chat">💬 CHAT</a>
            <a href="/leaderboard">🏆 LEADERBOARD</a>
        </div>
    </div>
    
    <div class="hero">
        <h1>ENTER THE MATRIX</h1>
        <p>THE ULTIMATE ANONYMOUS HACKING PLAYGROUND</p>
        <div>
            <a href="/quick-login" class="btn btn-primary">🚀 START HACKING</a>
            <a href="/games" class="btn btn-cyan">🎮 PLAY GAMES</a>
            <button onclick="anonymousLogin()" class="btn btn-danger">🕶️ ANONYMOUS MODE</button>
        </div>
    </div>
    
    <div class="features">
        <div class="feature-card card-games" onclick="window.location='/games'">
            <h3>🎮 HACKING GAMES</h3>
            <p>Test your skills with realistic hacking challenges, CTFs, and security puzzles.</p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li>Password Cracking</li>
                <li>Network Penetration</li>
                <li>Cryptography</li>
                <li>Binary Exploitation</li>
                <li>CTF Challenges</li>
            </ul>
        </div>
        
        <div class="feature-card card-terminal" onclick="window.location='/terminal'">
            <h3>💻 TERMINAL SIMULATOR</h3>
            <p>Practice real terminal commands in a safe, simulated Linux environment.</p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li>Linux Command Line</li>
                <li>Network Scanning</li>
                <li>File System Navigation</li>
                <li>Script Execution</li>
                <li>System Administration</li>
            </ul>
        </div>
        
        <div class="feature-card card-chat" onclick="window.location='/chat'">
            <h3>💬 ENCRYPTED CHAT</h3>
            <p>Communicate securely with hackers worldwide using military-grade encryption.</p>
            <ul style="margin-top: 15px; padding-left: 20px;">
                <li>End-to-End Encryption</li>
                <li>Anonymous Chatrooms</li>
                <li>File Sharing</li>
                <li>Voice Channels</li>
                <li>Group Discussions</li>
            </ul>
        </div>
        
        <div class="feature-card card-leaderboard" onclick="window.location='/leaderboard'">
            <h3>🏆 GLOBAL LEADERBOARD</h3>
            <p>Compete with hackers worldwide and climb to the top of the rankings.</p>
            <div id="leaderboard-preview">
                <!-- Filled by JavaScript -->
            </div>
        </div>
    </div>
    
    <div class="leaderboard">
        <h2 style="text-align: center; font-size: 2.5rem; margin-bottom: 30px; color: #ff0000;">
            TOP HACKERS
        </h2>
        <table>
            <thead>
                <tr>
                    <th>RANK</th>
                    <th>USERNAME</th>
                    <th>POINTS</th>
                    <th>TITLE</th>
                </tr>
            </thead>
            <tbody id="leaderboard-table">
                <!-- Filled by JavaScript -->
            </tbody>
        </table>
    </div>
    
    <div class="stats">
        <span id="online-status" style="color: #00ff00;">● ONLINE</span>
        | Players: <span id="player-count">1000+</span>
        | Uptime: <span id="uptime">99.9%</span>
    </div>
    
    <script>
        // Matrix effect
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        
        const chars = '01';
        const fontSize = 16;
        let columns = canvas.width / fontSize;
        let drops = [];
        
        function initMatrix() {
            columns = canvas.width / fontSize;
            drops = Array(Math.floor(columns)).fill(1);
        }
        
        initMatrix();
        
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.fillStyle = '#0F0';
            ctx.font = `${fontSize}px monospace`;
            
            for(let i = 0; i < drops.length; i++) {
                const char = chars[Math.floor(Math.random() * chars.length)];
                ctx.fillText(char, i * fontSize, drops[i] * fontSize);
                
                if(drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        
        setInterval(drawMatrix, 35);
        
        // Load leaderboard
        fetch('/api/leaderboard?limit=5')
            .then(r => r.json())
            .then(data => {
                const preview = document.getElementById('leaderboard-preview');
                preview.innerHTML = data.slice(0, 3).map((user, i) => `
                    <p>${i + 1}. ${user.username} - ${user.points}pts (${user.rank})</p>
                `).join('');
                
                const table = document.getElementById('leaderboard-table');
                table.innerHTML = data.map((user, i) => `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${user.username}</td>
                        <td>${user.points}</td>
                        <td>${user.rank}</td>
                    </tr>
                `).join('');
            });
        
        // Load stats
        fetch('/api/stats')
            .then(r => r.json())
            .then(stats => {
                document.getElementById('player-count').textContent = stats.total_players;
                document.getElementById('uptime').textContent = stats.uptime;
            });
        
        // Anonymous login
        async function anonymousLogin() {
            const response = await fetch('/api/quick-login', { method: 'POST' });
            const data = await response.json();
            if(data.status === 'success') {
                alert(`Welcome ${data.username}! You are now in ghost mode.`);
                window.location.reload();
            }
        }
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            fetch('/api/health').catch(() => {});
        }, 30000);
    </script>
</body>
</html>
'''

# ========== API ENDPOINTS ==========
@app.route('/')
def index():
    """Main page"""
    return render_template_string(MAIN_PAGE)

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        "status": "online",
        "service": "HackArena",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": round(time.time() - app.start_time, 2) if hasattr(app, 'start_time') else 0
    })

@app.route('/api/stats')
def stats():
    """Get statistics"""
    return jsonify({
        "total_players": len(db.users) + 1000,
        "online_now": len(db.online_users) + 50,
        "total_games": sum(len(games) for games in db.games.values() if isinstance(games, list)),
        "total_messages": sum(len(messages) for messages in db.messages.values()),
        "uptime": "99.9%",
        "server_load": "optimal"
    })

@app.route('/api/leaderboard')
def leaderboard():
    """Get leaderboard"""
    limit = request.args.get('limit', 100, type=int)
    return jsonify(db.leaderboard[:limit])

@app.route('/api/quick-login', methods=['POST'])
def quick_login():
    """Anonymous login"""
    session_id = secrets.token_hex(16)
    username = f"ghost_{secrets.token_hex(4)}"
    
    db.users[session_id] = {
        "username": username,
        "points": 0,
        "rank": "👤 Ghost",
        "level": 1,
        "created": time.time()
    }
    
    db.online_users.add(username)
    
    return jsonify({
        "status": "success",
        "message": "Logged in anonymously",
        "session_id": session_id,
        "username": username,
        "points": 0,
        "rank": "👤 Ghost"
    })

@app.route('/games')
def games_page():
    """Games page"""
    games_list = []
    for game_id, game_data in db.games.items():
        games_list.append({
            "id": game_id,
            **game_data
        })
    
    return jsonify({
        "status": "success",
        "games": games_list,
        "total_games": len(games_list)
    })

@app.route('/api/games/<game_id>', methods=['GET', 'POST'])
def game_handler(game_id):
    """Handle game requests"""
    if game_id not in db.games:
        return jsonify({"error": "Game not found"}), 404
    
    if request.method == 'GET':
        # Start new game
        game_session = {
            "id": secrets.token_hex(8),
            "game": game_id,
            "started": time.time(),
            "completed": False,
            "score": 0
        }
        
        # Add game-specific data
        if game_id == "password_cracker":
            game_session["challenge"] = {
                "hash": hashlib.md5(b"hackarena123").hexdigest(),
                "hint": "Contains 'hackarena' and numbers"
            }
        elif game_id == "network_scanner":
            game_session["network"] = f"10.0.{random.randint(1, 255)}.0/24"
        
        return jsonify(game_session)
    
    else:  # POST - Submit game results
        data = request.json
        score = data.get("score", 0)
        
        # Update user if logged in
        user_id = data.get("session_id")
        if user_id in db.users:
            db.users[user_id]["points"] += score
        
        return jsonify({
            "status": "success",
            "score": score,
            "message": "Game completed!"
        })

@app.route('/terminal')
def terminal_page():
    """Terminal interface"""
    return jsonify({
        "terminal": "active",
        "welcome": "Welcome to HackArena Terminal v3.0",
        "commands": [
            {"cmd": "help", "desc": "Show available commands"},
            {"cmd": "ls", "desc": "List files"},
            {"cmd": "scan <target>", "desc": "Scan network"},
            {"cmd": "crack <hash>", "desc": "Crack password hash"},
            {"cmd": "decode <file>", "desc": "Decode file"},
            {"cmd": "whoami", "desc": "Show user info"},
            {"cmd": "clear", "desc": "Clear terminal"}
        ]
    })

@app.route('/api/terminal/execute', methods=['POST'])
def execute_command():
    """Execute terminal command"""
    data = request.json
    command = data.get("command", "").strip().lower()
    
    responses = {
        "help": "Available commands: ls, scan, crack, decode, whoami, clear",
        "ls": "flag.txt\nsecret.txt\nnetwork.txt\nuser.txt\nsystem.log\nroot.txt",
        "scan 10.0.0.0/24": "Scanning...\n10.0.0.1 - Gateway\n10.0.0.100 - Target Server (Ports: 22, 80, 443, 8080)\n10.0.0.150 - Your Machine",
        "crack 5f4dcc3b5aa765d61d8327deb882cf99": "Cracking MD5...\nPassword: password\nTime: 2.3s",
        "decode secret.enc": "Decoding...\nMessage: 'The encryption key is: HACKARENA_ULTIMATE_2024'",
        "whoami": "User: anonymous\nRank: Ghost\nPoints: 0\nAccess: Level 1",
        "clear": ""
    }
    
    response = responses.get(command, f"Command not found: {command}\nType 'help' for available commands.")
    
    return jsonify({
        "command": command,
        "output": response,
        "timestamp": time.time()
    })

@app.route('/chat')
def chat_page():
    """Chat interface"""
    return jsonify({
        "chat": "active",
        "rooms": ["#general", "#hacking", "#ctf", "#help", "#announcements"],
        "online": list(db.online_users)[:20],
        "total_online": len(db.online_users)
    })

@app.route('/api/chat/send', methods=['POST'])
def send_message():
    """Send chat message"""
    data = request.json
    username = data.get("username", f"user_{secrets.token_hex(4)}")
    message = data.get("message", "")
    room = data.get("room", "#general")
    
    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    msg = {
        "id": secrets.token_hex(8),
        "username": username,
        "message": message,
        "room": room,
        "timestamp": datetime.utcnow().isoformat(),
        "encrypted": data.get("encrypted", False)
    }
    
    db.messages[room].append(msg)
    if len(db.messages[room]) > 100:
        db.messages[room] = db.messages[room][-100:]
    
    return jsonify({
        "status": "sent",
        "message_id": msg["id"]
    })

@app.route('/api/chat/messages')
def get_messages():
    """Get chat messages"""
    room = request.args.get("room", "#general")
    limit = int(request.args.get("limit", 50))
    
    messages = db.messages.get(room, [])[-limit:]
    
    return jsonify({
        "room": room,
        "messages": messages,
        "count": len(messages)
    })

@app.route('/leaderboard')
def leaderboard_page():
    """Leaderboard page"""
    return jsonify({
        "leaderboard": db.leaderboard,
        "updated": time.time()
    })

# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "not_found",
        "message": "The requested resource was not found",
        "suggestion": "Try /api/health to check server status"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "internal_error",
        "message": "An internal server error occurred",
        "timestamp": datetime.utcnow().isoformat()
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "error": "unexpected_error",
        "message": str(e),
        "type": type(e).__name__
    }), 500

# ========== INITIALIZATION ==========
@app.before_first_request
def initialize():
    app.start_time = time.time()
    print(f"HackArena started at {datetime.utcnow().isoformat()}")

# Vercel requires this
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
else:
    application = app
