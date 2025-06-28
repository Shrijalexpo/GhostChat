# GhostChat - Anonymous Telegram Bot 👻💬

<div align="center">

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API%20v2.0+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

*A sophisticated anonymous chatting bot for Telegram with priority-based matching, VIP membership, and email verification*

[Features](#-features) • [Installation](#-installation) • [Deployment](#-deployment) • [Usage](#-usage) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

GhostChat is a feature-rich Python-based Telegram bot that enables **anonymous communication** between users. Built with a modular architecture, it supports priority-based matching, organization-specific connections, referral-based VIP membership, and robust email verification using Gmail SMTP.

### 🎯 Primary Use Cases

- **Anonymous Social Networking** - Perfect for shy or introverted individuals
- **Professional Networking** - Cross-organizational communication
- **Language Exchange** - Cultural and linguistic communication practice  
- **Educational Tool** - Safe space for practicing communication skills

---

## ✨ Features

### 🔐 **Security & Verification**
- **Email OTP Verification** - Gmail SMTP integration for secure user verification
- **Anonymous Messaging** - Complete privacy protection for users
- **Report System** - Built-in user reporting and moderation tools

### 🎯 **Smart Matching System**
- **Priority-Based Algorithm** - VIP users get higher matching priority
- **Gender Preferences** - Customizable matching preferences
- **Organization Matching** - Domain-based matching for colleagues/classmates
- **Compatibility Checking** - Advanced user compatibility algorithms

### 👑 **VIP Membership System**
- **Referral-Based** - Earn VIP status by referring 5 users
- **30-Day Duration** - Automatic membership expiry management
- **Premium Benefits** - Higher priority, faster connections, premium features
- **Automatic Downgrade** - Seamless transition back to free tier

### 💬 **Rich Media Support**
- Text messages and emojis
- Photos and images (JPG, PNG)
- Documents and files (PDF, DOC, etc.)
- Voice messages and audio
- Videos and GIFs
- Stickers and location sharing
- Message editing support

### 📊 **Analytics & Management**
- User statistics and referral tracking
- Lobby management system
- Match success tracking
- Comprehensive logging system

---

## 🛠️ Installation

### Prerequisites

- **Python 3.7+**
- **Git**
- **Gmail account** with 2-Factor Authentication enabled
- **Telegram Bot Token** from [@BotFather](https://t.me/botfather)

### 1. Clone the Repository

```bash
git clone https://github.com/Shrijalexpo/GhostChat.git
cd GhostChat
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Gmail App Password Setup

1. **Enable 2-Step Verification** in your Google Account Security settings
2. **Generate App Password**:
   - Go to [App Passwords](https://myaccount.google.com/apppasswords) in Google Security
   - Select "Other (Custom name)", enter "GhostChat Bot"
   - **Copy the 16-character password** (save it securely - won't be shown again)

### 4. Environment Configuration

#### Linux/macOS:
```bash
export SENDER_EMAIL="your-email@gmail.com"
export APP_PASSWORD="your-16-character-app-password"
export BOT_TOKEN="your-telegram-bot-token"
```

#### Windows Command Prompt:
```cmd
set SENDER_EMAIL=your-email@gmail.com
set APP_PASSWORD=your-16-character-app-password
set BOT_TOKEN=your-telegram-bot-token
```

---

## 🚀 Deployment

### Local Development

```bash
python3 main.py
```

Monitor console output for errors and test functionality via Telegram.

### Production Deployment (AWS EC2)

#### 1. Launch EC2 Instance
- **OS**: Amazon Linux 2 or Ubuntu 20.04 LTS
- **Instance Type**: t2.micro (free tier eligible)
- **Security Group**: Allow SSH (port 22) and optionally HTTPS (port 443)

#### 2. Connect to EC2
```bash
# Amazon Linux 2
ssh -i your-key.pem ec2-user@your-instance-ip

# Ubuntu
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 3. Prepare Server Environment

**Amazon Linux 2:**
```bash
sudo yum update -y
sudo yum install python3 python3-pip git tmux -y
```

**Ubuntu:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git tmux -y
```

#### 4. Deploy Bot
```bash
git clone https://github.com/Shrijalexpo/GhostChat.git
cd GhostChat
python3 -m pip install -r requirements.txt
```

#### 5. 24/7 Operation with tmux

```bash
# Create persistent session
tmux new -s ghostchat

# Set environment variables
export SENDER_EMAIL="your-email@gmail.com"
export APP_PASSWORD="your-16-character-app-password"  
export BOT_TOKEN="your-telegram-bot-token"

# Start the bot
python3 main.py

# Detach from session (Ctrl+b, then d)
# Bot continues running in background
```

**Managing tmux sessions:**
```bash
# List sessions
tmux list-sessions

# Reattach to session
tmux attach -t ghostchat

# Kill session
tmux kill-session -t ghostchat
```

---

## 📝 Usage

### User Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and register |
| `/connect` | Find a random chat partner |
| `/disconnect` | End current chat session |
| `/next` | Skip current partner, find new one |
| `/settings` | Manage preferences and settings |
| `/refer` | Get referral link for VIP membership |
| `/stats` | View profile and referral statistics |
| `/report` | Report current partner |
| `/help` | Show all available commands |
| `/issue` | Report bugs or issues |

### Bot Features

- **Anonymous Matching** - Connect with random users based on preferences
- **Gender Filtering** - Choose to match with specific genders or anyone
- **Organization Matching** - Connect with people from your company/university
- **VIP Priority** - VIP members get matched faster with premium features
- **Media Sharing** - Share photos, documents, voice messages, and more
- **Message Editing** - Edit sent messages (partner sees edited version)

---

## 🏗️ Architecture

### Core Components

```
GhostChat/
├── main.py              # Main bot loop and startup
├── get_updates.py       # Message handling and routing
├── send_updates.py      # Telegram API communication
├── email_verification.py # OTP verification system
├── user_json.py         # User data management
├── lobby.py             # Matching queue management
├── match.py             # Matching algorithm
├── referral.py          # VIP membership system
├── root_json.py         # Bot configuration
├── log.py               # Logging system
├── requirements.txt     # Python dependencies
└── Json Files/          # Data storage
    ├── users.json       # User profiles
    ├── lobby.json       # Active lobby
    ├── matches.json     # Current matches
    ├── referrals.json   # Referral tracking
    └── root.json        # Bot settings
```

### System Flow

1. **User Registration** → Email verification → Profile creation
2. **Lobby System** → Priority-based matching → Connection establishment  
3. **Chat Session** → Media support → Session management
4. **Referral System** → VIP upgrade → Enhanced features

---

## 🔧 Configuration

### Email Settings
Update `email_verification.py` with your Gmail credentials:
```python
SENDER_EMAIL = 'your-email@gmail.com'
SENDER_PASSWORD = 'your-app-password'
```

### Bot Settings
Configure bot parameters in `root_json.py`:
- Telegram Bot Token
- Update polling timeout
- Command prefix

---

## 📊 Monitoring & Logs

The bot automatically generates daily log files in the `logs/` directory:

```bash
# View today's logs
tail -f logs/log_$(date +%Y-%m-%d).txt

# Monitor bot activity
grep "MATCH" logs/log_$(date +%Y-%m-%d).txt
grep "ERROR" logs/log_$(date +%Y-%m-%d).txt
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive logging for new features
- Update documentation for any API changes
- Test thoroughly before submitting PR

---

## 📋 Roadmap

- [ ] **Database Migration** - PostgreSQL/MongoDB support
- [ ] **Web Dashboard** - Admin panel for bot management
- [ ] **Multi-language Support** - Internationalization
- [ ] **Voice/Video Calls** - WebRTC integration
- [ ] **Mobile App** - Native iOS/Android companion
- [ ] **AI Moderation** - Automated content filtering
- [ ] **Group Chats** - Multi-user anonymous rooms

---

## 🐛 Troubleshooting

### Common Issues

**Bot not responding:**
- Verify bot token is correct
- Check internet connectivity
- Review log files for errors

**Email verification failing:**
- Ensure 2FA is enabled on Gmail
- Verify app password is correct
- Check Gmail security settings

**Matching not working:**
- Confirm users are in lobby
- Check compatibility settings
- Review matching algorithm logs

**AWS EC2 Issues:**
- Verify security group settings
- Check tmux session status
- Monitor server resources

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Shrijalexpo**
- GitHub: [@Shrijalexpo](https://github.com/Shrijalexpo)
- Project Link: [GhostChat](https://github.com/Shrijalexpo/GhostChat)

---

## 🙏 Acknowledgments

- [Telegram Bot API](https://core.telegram.org/bots/api) for excellent documentation
- [Python Telegram Bot](https://python-telegram-bot.org/) community for inspiration
- Contributors and users who help improve the bot

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

[Report Bug](https://github.com/Shrijalexpo/GhostChat/issues) • [Request Feature](https://github.com/Shrijalexpo/GhostChat/issues) • [Documentation](https://github.com/Shrijalexpo/GhostChat/wiki)

</div>
