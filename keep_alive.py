from flask import Flask, render_template_string
from threading import Thread

app = Flask('')

# Beautiful, modern dark-themed HTML/CSS dashboard directly in the code
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ly's AI - Official Documentation & Tutorial</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f111a;
            color: #e2e8f0;
            margin: 0;
            padding: 0;
        }
        header {
            background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
            padding: 40px 20px;
            text-align: center;
            border-bottom: 2px solid #4338ca;
        }
        header h1 {
            margin: 0;
            font-size: 2.5rem;
            color: #5865F2; /* Discord Blue */
        }
        header p {
            color: #94a3b8;
            font-size: 1.1rem;
            margin-top: 10px;
        }
        .container {
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
        }
        .section {
            background-color: #1e293b;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        h2 {
            color: #38bdf8;
            margin-top: 0;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
        }
        .command-list {
            list-style: none;
            padding: 0;
        }
        .command-item {
            background-color: #0f172a;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 12px;
            border-left: 4px solid #5865F2;
        }
        .command-name {
            font-family: 'Courier New', Courier, monospace;
            font-weight: bold;
            color: #f43f5e;
            font-size: 1.1rem;
        }
        .command-desc {
            margin-top: 5px;
            color: #cbd5e1;
        }
        .badge {
            background-color: #dc2626;
            color: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <header>
        <h1>✨ Ly's AI Commands Dashboard</h1>
        <p>The complete user tutorial and command layout encyclopedia.</p>
    </header>

    <div class="container">
        
        <div class="section">
            <h2>🧠 1. Interactive AI Core</h2>
            <p>Ly's AI comes equipped with a continuous smart short-term memory vault. It tracks conversations dynamically per user.</p>
            <ul class="command-list">
                <li class="command-item">
                    <span class="command-name">/ai [prompt]</span>
                    <div class="command-desc">Initiates or continues a conversational back-and-forth thread with the Llama 3.3 engine.</div>
                </li>
                <li class="command-item">
                    <span class="command-name">/ai_forget</span>
                    <div class="command-desc">Instantly clears out the bot's temporary storage data regarding your past prompts to start a completely fresh context thread.</div>
                </li>
            </ul>
        </div>

        <div class="section">
            <h2>🎫 2. Server Ticket Operations</h2>
            <p>Need support or looking to challenge a server action? Use our dedicated ticket processing commands.</p>
            <ul class="command-list">
                <li class="command-item">
                    <span class="command-name">/appeal [username] [reason]</span>
                    <div class="command-desc">Generates an isolated, secure channel visible only to you and administrative staff members to challenge server restrictions or Roblox enforcement actions.</div>
                </li>
                <li class="command-item">
                    <span class="command-name">/ticket [type] [details]</span>
                    <div class="command-desc">Routes system bugs, feedback data, or general upgrade requests directly to the core development account.</div>
                </li>
            </ul>
        </div>

        <div class="section">
            <h2>🎉 3. Entertainment & Utilities</h2>
            <p>Keep your chat channels highly interactive with gaming commands.</p>
            <ul class="command-list">
                <li class="command-item">
                    <span class="command-name">/joke</span> - Returns a randomly selected comedic one-liner.
                </li>
                <li class="command-item">
                    <span class="command-name">/vibecheck [user]</span> - Scores a selected member's aura metrics from 0% to 100%.
                </li>
                <li class="command-item">
                    <span class="command-name">/slap [user]</span> - Playfully targets a user with a cold fish action animation banner.
                </li>
            </ul>
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
