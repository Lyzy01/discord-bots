from flask import Flask, render_template_string
from threading import Thread

app = Flask('')

# Deep space/cyberpunk dark theme dashboard with modern interactive elements
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ly's AI Hub — Core Systems Panel</title>
    <style>
        /* Modern Reset and Smooth Scrolling */
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

        /* Ambient background glow effects */
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

        body::after {
            content: '';
            position: absolute;
            bottom: 10%;
            right: -5%;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, transparent 60%);
            z-index: -1;
            pointer-events: none;
        }

        /* Entry Fade-In Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulseNeon {
            0%, 100% { border-color: rgba(168, 85, 247, 0.4); box-shadow: 0 0 15px rgba(168, 85, 247, 0.1); }
            50% { border-color: rgba(56, 189, 248, 0.7); box-shadow: 0 0 25px rgba(56, 189, 248, 0.2); }
        }

        /* Header / Hero Section Section */
        header {
            padding: 80px 20px 60px 20px;
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

        /* Container & Grid Elements */
        .container {
            max-width: 1000px;
            margin: 0 auto 80px auto;
            padding: 0 25px;
        }

        .section {
            background: rgba(22, 28, 45, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 35px;
            margin-bottom: 35px;
            animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.2s backwards;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease, box-shadow 0.4s ease;
        }

        /* Special continuous subtle glow for the top card */
        .section.ai-pulse {
            animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) 0.1s backwards, pulseNeon 6s infinite;
        }

        .section:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
        }

        h2 {
            font-size: 1.6rem;
            font-weight: 700;
            color: #38bdf8;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .sec-desc {
            color: #94a3b8;
            font-size: 1rem;
            margin-bottom: 25px;
        }

        /* Lists and Commands Design layout */
        .command-list {
            list-style: none;
        }

        .command-item {
            background: rgba(10, 11, 16, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.03);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .command-item:last-child {
            margin-bottom: 0;
        }

        .command-item:hover {
            background: rgba(15, 23, 42, 0.8);
            border-left: 4px solid #a855f7;
            padding-left: 24px;
            transform: translateX(4px);
        }

        .command-header {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }

        .command-name {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
            font-weight: 700;
            color: #f43f5e;
            font-size: 1.1rem;
            letter-spacing: -0.5px;
        }

        .badge {
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.2);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .badge.admin-tag {
            background: rgba(244, 63, 94, 0.1);
            color: #f43f5e;
            border: 1px solid rgba(244, 63, 94, 0.2);
        }

        .command-desc {
            color: #cbd5e1;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* Custom scrollbar to match the cool atmosphere */
        ::-webkit-scrollbar {
            width: 100px;
            max-width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #0a0b10;
        }
        ::-webkit-scrollbar-thumb {
            background: #1e293b;
            border-radius: 10px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #334155;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-glow">Ly's AI Terminal</div>
        <p>The premium, custom interface manual. Outfitted with short-term user isolation engines and security routing clusters.</p>
    </header>

    <div class="container">
        
        <div class="section ai-pulse">
            <h2>🧠 Conversational Intelligence Vault</h2>
            <div class="sec-desc">Powered by an advanced dynamic dictionary storage cluster. Remembers past prompts sequentially per account identity.</div>
            
            <div class="command-list">
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/ai [prompt]</span>
                        <span class="badge">Active Memory</span>
                    </div>
                    <div class="command-desc">Transmits queries into Ly's specialized dialogue stack. Keeps context across multiple continuous replies.</div>
                </div>
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/ai_forget</span>
                        <span class="badge">Data Purge</span>
                    </div>
                    <div class="command-desc">Instantly cleanses your short-term dialogue storage bank, prompting a clean structural context reboot.</div>
                </div>
            </div>
        </div>

        <div class="section" style="animation-delay: 0.3s;">
            <h2>🛡️ Infrastructure Integrity Center</h2>
            <div class="sec-desc">Secure data pipelines running straight to high staff entities or directly to core systems developers.</div>
            
            <div class="command-list">
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/adduiplayerreport [channel]</span>
                        <span class="badge admin-tag">Operator Only</span>
                    </div>
                    <div class="command-desc">Deploys an automated incident report drop point. Spawns private, multi-button secure channels when users file infractions.</div>
                </div>
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/adduiappealban [channel]</span>
                        <span class="badge admin-tag">Operator Only</span>
                    </div>
                    <div class="command-desc">Drops the official account enforcement appeal terminal. Spawns secure evaluation corridors for restricted entities.</div>
                </div>
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/ticket [type] [details]</span>
                        <span class="badge">Direct Feed</span>
                    </div>
                    <div class="command-desc">Transmits critical bugs, layout configurations, or direct feature recommendations completely into the core developer's personal layout feeds.</div>
                </div>
            </div>
        </div>

        <div class="section" style="animation-delay: 0.4s;">
            <h2>⚡ Interactive Protocol Utilities</h2>
            <div class="sec-desc">Fast, auxiliary operational routines to entertain server members or check profile aura data.</div>
            
            <div class="command-list">
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/vibecheck [user]</span>
                        <span class="badge">Analytics</span>
                    </div>
                    <div class="command-desc">Runs automated aura metrics to score a selected server user's current synchronization percentages.</div>
                </div>
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/joke</span>
                        <span class="badge">Entertainment</span>
                    </div>
                    <div class="command-desc">Pulls an automated humor routine output directly into the text frame channels.</div>
                </div>
                <div class="command-item">
                    <div class="command-header">
                        <span class="command-name">/website</span>
                        <span class="badge">Web Core</span>
                    </div>
                    <div class="command-desc">Generates a live connection link pointing right back to this encrypted user tutorial panel dashboard.</div>
                </div>
            </div>
        </div>

    </div>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
