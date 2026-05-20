from flask import Flask, render_template_string
from threading import Thread

app = Flask('')

# Dynamic global dictionary holding real-time bot information
LIVE_STATS = {
    "servers": 921,     # Automatically calculated and updated via tickets.py
    "users": "Active",   # Displays active counters rather than blank slots
    "processed": 326
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ly's AI Hub — Core Operations Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0a0b10;
            --bg-card: rgba(22, 28, 45, 0.4);
            --bg-accent: rgba(10, 11, 16, 0.6);
            --text-primary: #f1f5f9;
            --text-muted: #94a3b8;
            --accent-purple: #a855f7;
            --accent-cyan: #38bdf8;
            --accent-danger: #f43f5e;
            --accent-success: #10b981;
            --border-color: rgba(255, 255, 255, 0.05);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            scroll-behavior: smooth;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-primary);
            overflow-x: hidden;
            line-height: 1.6;
        }

        /* Ambient Background Glow Effect */
        body::before {
            content: '';
            position: fixed;
            top: -10%;
            left: -10%;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, transparent 70%);
            z-index: -1;
            pointer-events: none;
        }

        /* Keyframe Animations */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(25px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulseNeon {
            0%, 100% { border-color: rgba(168, 85, 247, 0.3); box-shadow: 0 0 15px rgba(168, 85, 247, 0.05); }
            50% { border-color: rgba(56, 189, 248, 0.6); box-shadow: 0 0 25px rgba(56, 189, 248, 0.15); }
        }

        header {
            padding: 80px 20px 40px 20px;
            text-align: center;
            background: radial-gradient(ellipse at bottom, #111026 0%, #0a0b10 100%);
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .logo-glow {
            font-size: 3.5rem;
            font-weight: 800;
            letter-spacing: -1.5px;
            background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 15px;
            display: inline-block;
        }

        header p {
            color: var(--text-muted);
            font-size: 1.15rem;
            max-width: 650px;
            margin: 0 auto;
        }

        /* Metrics Row Layout */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            max-width: 1050px;
            margin: -10px auto 40px auto;
            padding: 0 25px;
            animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 22px;
            text-align: center;
            backdrop-filter: blur(10px);
            transition: border-color 0.3s ease;
        }

        .stat-card:hover {
            border-color: rgba(56, 189, 248, 0.2);
        }

        .stat-val {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--accent-cyan);
            font-family: 'JetBrains Mono', monospace;
        }

        .stat-lbl {
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 5px;
        }

        .container {
            max-width: 1050px;
            margin: 0 auto 80px auto;
            padding: 0 25px;
        }

        /* Safety Assurance Panel Banner */
        .safety-banner {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.04) 0%, rgba(22, 28, 45, 0.3) 100%);
            border: 1px solid rgba(16, 185, 129, 0.15);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 35px;
            display: flex;
            align-items: center;
            gap: 20px;
            animation: fadeInUp 0.9s ease-out;
        }

        .safety-icon {
            font-size: 2.2rem;
            color: var(--accent-success);
            background: rgba(16, 185, 129, 0.08);
            padding: 10px 15px;
            border-radius: 12px;
        }

        .safety-text h3 {
            color: var(--accent-success);
            font-size: 1.15rem;
            margin-bottom: 4px;
            font-weight: 600;
        }

        .safety-text p {
            color: var(--text-muted);
            font-size: 0.95rem;
        }

        /* Split Left / Right Component Grid */
        .split-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 30px;
            margin-bottom: 35px;
        }

        @media (max-width: 900px) {
            .split-grid { grid-template-columns: 1fr; }
        }

        .section {
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 35px;
            animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.4s ease;
        }

        .section.ai-pulse {
            animation: pulseNeon 6s infinite ease-in-out;
        }

        .section:hover {
            transform: translateY(-4px);
            border-color: rgba(255, 255, 255, 0.1);
        }

        h2 {
            font-size: 1.5rem;
            color: var(--accent-cyan);
            margin-bottom: 8px;
            font-weight: 600;
        }

        .sec-desc {
            color: var(--text-muted);
            margin-bottom: 25px;
            font-size: 0.95rem;
        }

        /* Commands and Instruction Steps */
        .command-item, .step-item {
            background: var(--bg-accent);
            border: 1px solid rgba(255, 255, 255, 0.02);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }

        .command-item:last-child, .step-item:last-child {
            margin-bottom: 0;
        }

        .command-item:hover {
            background: rgba(15, 23, 42, 0.6);
            border-left: 4px solid var(--accent-purple);
            transform: translateX(4px);
        }

        .command-name {
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: var(--accent-danger);
            font-size: 1.05rem;
        }

        .command-desc {
            color: #cbd5e1;
            font-size: 0.95rem;
            margin-top: 5px;
        }

        /* Step Instruction Variations */
        .step-item {
            display: flex;
            gap: 15px;
        }

        .step-num {
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-purple);
            background: rgba(168, 85, 247, 0.1);
            font-weight: bold;
            font-size: 0.85rem;
            width: 26px;
            height: 26px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }

        .step-text h4 {
            font-size: 1rem;
            color: #ffffff;
            margin-bottom: 4px;
        }

        .step-text p {
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        .code-tag {
            font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 0, 0, 0.4);
            color: var(--accent-cyan);
            padding: 1px 6px;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        /* Permissions Layout list */
        .perm-wrapper {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .perm-card {
            background: var(--bg-accent);
            padding: 15px;
            border-radius: 10px;
        }

        .perm-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }

        .perm-title {
            font-weight: 600;
            font-size: 0.95rem;
        }

        .perm-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            padding: 2px 8px;
            border-radius: 6px;
        }

        .badge-req { background: rgba(244, 63, 94, 0.1); color: var(--accent-danger); }
        .badge-opt { background: rgba(56, 189, 248, 0.1); color: var(--accent-cyan); }

        .perm-text {
            color: var(--text-muted);
            font-size: 0.85rem;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-glow">Ly's AI Hub</div>
        <p>Premium automation layout control center. Configured with structural context processing, multi-button panel views, and backend data routing clusters.</p>
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

        <div class="safety-banner">
            <div class="safety-icon">🛡️</div>
            <div class="safety-text">
                <h3>Ethical Core System Integrity Policy</h3>
                <p>This system framework serves exclusively as an administrative support suite. It contains absolute programmatic safety boundaries, completely avoiding arbitrary background executions, hostile mechanisms, or harmful modifications to server environments.</p>
            </div>
        </div>

        <div class="split-grid">
            
            <div class="section">
                <h2>📖 Interactive Ticket & Triage User Manual</h2>
                <div class="sec-desc">How to open, manage, and process cases smoothly using our custom integration channels:</div>
                
                <div class="step-item">
                    <div class="step-num">1</div>
                    <div class="step-text">
                        <h4>Filing an Incident Report</h4>
                        <p>Click the red <span class="code-tag">File Incident Report 🚩</span> button. A pop-up form will appear asking for the rule-breaker's name, situational details, and proof links.</p>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num">2</div>
                    <div class="step-text">
                        <h4>Submitting a Ban Appeal</h4>
                        <p>Click the blue <span class="code-tag">Request Case Review 📑</span> button. Enter your in-game details and context to explain your defense argument to the review team.</p>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num">3</div>
                    <div class="step-text">
                        <h4>Private Working Corridors</h4>
                        <p>Once submitted, a unique text channel (e.g., <span class="code-tag">#incident-username</span>) creates instantly. Only you and authorized server staff roles can read or type inside it.</p>
                    </div>
                </div>

                <div class="step-item">
                    <div class="step-num">4</div>
                    <div class="step-text">
                        <h4>Staff Resolution Center</h4>
                        <p>Moderators review the data using embedded control buttons. Clicking **Approve Case** or **Deny Case** notifies the user and completely files the logs away securely.</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔐 Bot Role & Permission Setup</h2>
                <div class="sec-desc">Ensure the system's integrated application role card possesses these properties in your server settings:</div>
                
                <div class="perm-wrapper">
                    <div class="perm-card">
                        <div class="perm-header">
                            <span class="perm-title">📁 Manage Channels</span>
                            <span class="perm-badge badge-req">Required</span>
                        </div>
                        <p class="perm-text">Allows the bot to automatically spin up, provision, and cleanly archive custom user ticket rooms.</p>
                    </div>

                    <div class="perm-card">
                        <div class="perm-header">
                            <span class="perm-title">💬 Send Messages</span>
                            <span class="perm-badge badge-req">Required</span>
                        </div>
                        <p class="perm-text">Enables transmission of operational dialogue forms, selection menus, and button controllers.</p>
                    </div>

                    <div class="perm-card">
                        <div class="perm-header">
                            <span class="perm-title">🔗 Embed Links</span>
                            <span class="perm-badge badge-req">Required</span>
                        </div>
                        <p class="perm-text">Necessary for formatting high-fidelity triage summaries and colored audit logs.</p>
                    </div>

                    <div class="perm-card">
                        <div class="perm-header">
                            <span class="perm-title">🛡️ Required Staff Roles</span>
                            <span class="perm-badge badge-opt">Important</span>
                        </div>
                        <p class="perm-text">Moderators must have a role containing the words <b>"admin"</b>, <b>"moderator"</b>, <b>"staff"</b>, or <b>"owner"</b> to operate panel closeout actions.</p>
                    </div>
                </div>
            </div>

        </div>

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
