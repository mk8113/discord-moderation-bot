# 🤖 Discord Bot — Moderation + AI + Games

A fully featured Discord bot built in Python with moderation tools, AI integration (OpenAI GPT-3.5), and fun mini-games.

---

## ✨ Features

### 🛡️ Moderation
| Command | Description | Permission |
|---|---|---|
| `!warn @user reason` | Warn a member | Manage Messages |
| `!warns @user` | Show warns | Manage Messages |
| `!clearwarns @user` | Clear warns | Administrator |
| `!mute @user` | Mute a member | Manage Roles |
| `!unmute @user` | Unmute a member | Manage Roles |
| `!kick @user reason` | Kick a member | Kick Members |
| `!ban @user reason` | Ban a member | Ban Members |
| `!unban name#0000` | Unban a member | Ban Members |
| `!clear 10` | Delete messages | Manage Messages |
| `!ticket` | Open a support ticket | Everyone |
| `!closeticket` | Close the ticket | Everyone |

### 🤖 AI
| Command | Description |
|---|---|
| `!ai your question` | Ask GPT-3.5 anything |

### 🎮 Mini-Games
| Command | Description |
|---|---|
| `!rps rock/paper/scissors` | Rock Paper Scissors |
| `!guess` | Number guessing game (1-100) |
| `!trivia` | General knowledge quiz |
| `!dice 6` | Roll a dice (2-100 faces) |
| `!coin` | Heads or tails |

### 📋 Automatic
- Welcome message on member join
- Auto-log of all actions in `#logs`
- Bot status displayed as "playing"

---

## ⚙️ Setup

### 1 — Requirements
- Python 3.10+
- A Discord Developer account
- (Optional) An OpenAI API key

### 2 — Clone the repo
```bash
git clone https://github.com/mk8113/discord-moderation-bot.git
cd discord-moderation-bot
```

### 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### 4 — Configure
Open `config.py` and replace:
```python
TOKEN = "YOUR_TOKEN_HERE"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
```

### 5 — Run
```bash
python bot.py
```

---

## 🔑 How to get a Discord Token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → give it a name
3. **Bot** → **Add Bot** → **Reset Token** → copy it
4. Enable the 3 **Privileged Gateway Intents**
5. **OAuth2 → URL Generator** → check `bot` + `Administrator`
6. Open the generated link to invite the bot

---

## 📁 File Structure

```
discord-moderation-bot/
├── bot.py            ← Main bot code
├── config.py         ← Token & settings
├── warns.json        ← Warn storage (auto-created)
├── requirements.txt  ← Dependencies
└── README.md         ← Documentation
```

---

## 🛠️ Built with

- **Python 3.10+**
- **discord.py** — Discord API wrapper
- **openai** — GPT-3.5 integration

---

## 📄 License

MIT — Free to use and modify.
