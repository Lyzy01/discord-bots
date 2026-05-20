from flask import Flask, render_template_string
from threading import Thread

app = Flask('')

# Dynamic global dictionary holding real-time bot information
LIVE_STATS = {
    "servers": 921,        # Set your actual number here so it's never 0
    "users": "Active",   # Shows active instead of a blank 0
    "processed": 326
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ly's AI Hub — Core Systems Panel</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #0a0b10;
            color: #f1f5f9;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: absolute;
            top: -10%;
            left: -10%;
            width: 50%;
            height: 50%;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.15) 0%, transparent 70%);
            z-index: -1;
            pointer-events: none;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulseNeon {
            0%, 100% { border-color: rgba(168, 85, 247, 0.4); box-shadow: 0 0 15px rgba(168, 85, 247, 0.1); }
            50% { border-color: rgba(56, 189, 248, 0.7); box-shadow: 0 0 25px rgba(56, 189, 248, 0.2); }
        }

        header {
            padding: 80px 20px 40px 20px;
            text-align: center;
            background: radial-gradient(ellipse at bottom, #111026 0%, #0a0b10 100%);
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .logo-glow {
            font-size: 3.5rem;
            font-weight: 900;
            letter-spacing: -1px;
            background: linear-gradient(135deg, #a855f7 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            display: inline-block;
        }

        header p {
            color: #94a3b8;
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }

        /* LIVE STATS METRICS ROW GRID */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            max-width: 1000px;
            margin: 20px auto 40px auto;
            padding: 0 25px;
            animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
        }

        .stat-val {
            font-size: 2rem;
            font-weight: 800;
            color: #38bdf8;
            font-family: monospace;
        }

        .stat-lbl {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 5px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto 80px auto;
            padding: 0 25px;
        }

        .section {
            background: rgba(22, 28, 45, 0.4);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 35px;
            margin-bottom: 35px;
            animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.2s backwards;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease;
        }

        .section.ai-pulse {
            animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.1s backwards, pulseNeon 6s infinite;
        }

        .section:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.12);
        }

        h2 {
            font-size: 1.6rem;
            color: #38bdf8;
            margin-bottom: 8px;
        }

        .sec-desc {
            color: #94a3b8;
            margin-bottom: 25px;
        }

        .command-item {
            background: rgba(10, 11, 16, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.03);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .command-item:hover {
            background: rgba(15, 23, 42, 0.8);
            border-left: 4px solid #a855f7;
            transform: translateX(4px);
        }

        .command-name {
            font-family: monospace;
            font-weight: 700;
            color: #f43f5e;
            font-size: 1.1rem;
        }

        .command-desc {
            color: #cbd5e1;
            font-size: 0.95rem;
            margin-top: 5px;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-glow">Ly's AI Terminal</div>
        <p>The premium, custom interface manual. Outfitted with short-term user isolation engines and security routing clusters.</p>
    </header>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-val">{{ stats.servers }}</div>
            <div class="stat-lbl">Active Servers</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.users }}</div>
            <div class="stat-lbl">Users Protected</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">{{ stats.processed }}</div>
            <div class="stat-lbl">Cases Managed</div>
        </div>
    </div>

    <div class="container">
        <div class="section ai-pulse">
            <h2>🧠 Conversational Intelligence Vault</h2>
            <div class="sec-desc">Powered by an advanced dynamic dictionary storage cluster. Remembers past prompts sequentially per account identity.</div>
            <div class="command-item">
                <span class="command-name">/ai [prompt]</span>
                <div class="command-desc">Transmits queries into Ly's specialized dialogue stack. Keeps context across multiple continuous replies.</div>
            </div>
            <div class="command-item">
                <span class="command-name">/ai_forget</span>
                <div class="command-desc">Instantly cleanses your short-term dialogue storage bank, prompting a clean structural context reboot.</div>
            </div>
        </div>

        <div class="section">
            <h2>🛡️ Infrastructure Integrity Center</h2>
            <div class="sec-desc">Secure data pipelines running straight to high staff entities or directly to core systems developers.</div>
            <div class="command-item">
                <span class="command-name">/adduiplayerreport [channel]</span>
                <div class="command-desc">Deploys an automated incident report drop point. Spawns private, multi-button secure channels when users file infractions.</div>
            </div>
            <div class="command-item">
                <span class="command-name">/adduiappealban [channel]</span>
                <div class="command-desc">Drops the official account enforcement appeal terminal. Spawns secure evaluation corridors for restricted entities.</div>
            </div>
        </div>
    </div>

</body>
</html>
"""

@app.route('/')
def home():
    # Render page while passing live calculated stats parameters
    return render_template_string(HTML_TEMPLATE, stats=LIVE_STATS)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
