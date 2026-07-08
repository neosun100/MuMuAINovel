[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/neosun100-mumuainovel-badge.png)](https://mseep.ai/app/neosun100-mumuainovel)

[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# MuMuAINovel 📚✨

**🚀 AI-Powered Novel Writing Assistant | Generate 1M+ Word Novels Automatically**

![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![React](https://img.shields.io/badge/react-18.3.1-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![API](https://img.shields.io/badge/API%20Endpoints-200+-orange.svg)

**⭐ If this project helps you, please give it a Star!**

</div>

---

## 🎯 Highlights

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-AI Support** | OpenAI / Gemini / Claude seamless switching |
| 📖 **Smart Chapter Generation** | RTCO framework for dynamic context, auto plot continuation |
| 🎭 **Character Management** | Relationship graphs, organization charts, growth tracking |
| 🔮 **Foreshadowing System** | Smart tracking, auto-injection during generation |
| 📊 **Quality Scoring** | Basic metrics + AI evaluation, S/A/B/C/D grading |
| 🔍 **Consistency Check** | AI analysis of character behavior and plot coherence |
| ⏱️ **Timeline Management** | Story event timeline tracking and visualization |
| 🎨 **Style Analysis** | Learn writing style, generate style guides for AI |
| 🔄 **Duplicate Detection** | Detect repetitive content within and across chapters |
| 💾 **PostgreSQL** | Production-grade database, 200+ concurrent users |
| 🚀 **Batch Generation** | Generate 100 chapters × 10,000 words automatically |

---

## ✨ Features

### Core Features

- 🤖 **Multi-AI Models** - Support OpenAI, Gemini, Claude, and custom API endpoints
- 📝 **Smart Wizard** - AI auto-generates outlines, characters, and worldview
- 👥 **Character Management** - Visual relationship and organization management
- 📖 **Chapter Editor** - Create, edit, regenerate, and polish chapters
- 🌐 **World Building** - Complete story background construction
- 💡 **Inspiration Mode** - AI-driven creative ideas generation
- ✍️ **Custom Styles** - Support custom AI writing styles
- 📊 **Mind Map** - Visualize chapter logic relationships

### Advanced Features (v1.3.0+)

- 🔮 **Foreshadowing Management** - Track plot foreshadowing, remind unresolved threads
- 🔍 **Consistency Detection** - AI analyzes character behavior and plot coherence
- ⏱️ **Timeline Management** - Story event timeline tracking
- 🎨 **Style Analysis** - Learn project writing style, generate style guides
- 📊 **Chapter Quality Scoring** - Basic metrics + AI comprehensive evaluation
- 🔄 **Duplicate Detection** - Detect repetitive/similar content
- 📈 **Character Growth** - Track character ability, relationship, psychology changes

---

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- At least one AI service API Key (OpenAI/Gemini/Claude)

### Docker Compose Deployment (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/neosun100/MuMuAINovel.git
cd MuMuAINovel

# 2. Configure environment variables
cp .env.example .env
# Edit .env file, fill in API Key and database password

# 3. Start services
docker-compose up -d

# 4. Access the application
# Open browser and visit http://localhost:8000
```

### Using Docker Hub Image

```bash
# Pull latest image (includes model files)
docker pull mumujie/mumuainovel:latest

# Configure and start
cp .env.example .env
docker-compose up -d
```

---

## ⚙️ Configuration

### Required Configuration (.env)

```bash
# PostgreSQL Database
DATABASE_URL=postgresql+asyncpg://mumuai:your_password@postgres:5432/mumuai_novel
POSTGRES_PASSWORD=your_secure_password

# AI Service (configure at least one)
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini

# Local Account Login
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password
```

### Optional Configuration

```bash
# LinuxDO OAuth
LINUXDO_CLIENT_ID=your_client_id
LINUXDO_CLIENT_SECRET=your_client_secret

# Gemini
GEMINI_API_KEY=your_gemini_key

# Claude
ANTHROPIC_API_KEY=your_anthropic_key

# Connection Pool (high concurrency)
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=30
```

---

## 📚 API Documentation

### API Overview

This project provides **200+ RESTful API endpoints** covering the entire novel creation workflow.

| Module | Endpoints | Description |
|--------|-----------|-------------|
| Auth | 8 | Login, OAuth, session management |
| Projects | 12 | Project CRUD, import/export |
| Outlines | 15 | Outline generation, editing, AI continuation |
| Characters | 18 | Character management, relationship graphs |
| Chapters | 25 | Chapter generation, editing, batch operations |
| Foreshadows | 10 | Foreshadowing tracking, resolution reminders |
| Consistency | 4 | Character/plot consistency detection |
| Timeline | 6 | Event timeline management |
| Style | 3 | Writing style learning and analysis |
| Quality | 2 | Chapter quality evaluation |
| Duplicate | 2 | Duplicate content detection |
| Growth | 6 | Character growth tracking |

### Online Documentation

After starting the service, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Novel Creation Pipeline

### Automated Workflow

MuMuAINovel supports fully automated novel creation through API:

```
1. POST /api/auth/local/login           # Login
2. POST /api/projects                    # Create project
3. PUT  /api/projects/{id}               # Set worldview
4. POST /api/characters (loop)           # Create characters (80-150)
5. POST /api/outlines (loop)             # Create outlines (100 chapters)
6. POST /api/chapters (loop)             # Create chapters (100)
7. POST /api/chapters/project/{id}/batch-generate  # Submit batch generation
8. GET  /api/chapters/project/{id}       # Monitor progress
```

### Key Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| count | 10 | 1-100 | Chapters to generate |
| target_word_count | 10000 | 1000-20000 | Words per chapter |
| max_retries | 10 | 0-20 | Max retry attempts |

### RTCO Context Framework

```
Chapter     Context Strategy
─────────────────────────────────
Chapter 1   Outline + Characters only
Ch 2-10     Previous chapter ending 300 chars + involved characters
Ch 11-50    Previous ending 500 chars + related memories 3
Ch 51+      Previous ending 500 chars + story skeleton + smart memories 5
```

### Retry Strategy (Staged Backoff)

| Retry Count | Wait Time | Description |
|-------------|-----------|-------------|
| 1-3 | 2, 4, 8 sec | Quick retry |
| 4-6 | 30 sec | Medium wait |
| 7-10 | 60 sec | Long wait |

---

## 🔄 Task Recovery

### Auto Recovery Script

```bash
# One-time recovery
python auto_resume.py

# Daemon mode (until all complete)
python auto_resume.py --daemon

# Background with logging
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### Environment Variables

```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

---

## 🔌 MCP Server (AI Assistant Integration)

MuMuAINovel provides an MCP (Model Context Protocol) server that allows AI assistants like Claude and Kiro to directly create novels.

### Installation

```bash
pip install mcp httpx
```

### Configuration (Claude Desktop)

Edit `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mumuai-novel": {
      "command": "python",
      "args": ["/path/to/MuMuAINovel/mcp_novel_server.py"],
      "env": {
        "MUMUAI_BASE_URL": "http://localhost:8000",
        "MUMUAI_USERNAME": "admin",
        "MUMUAI_PASSWORD": "your_password"
      }
    }
  }
}
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `novel_list_projects` | List all novel projects |
| `novel_create_project` | Create new project |
| `novel_create_characters_batch` | Batch create characters |
| `novel_create_outlines_batch` | Batch create outlines |
| `novel_batch_generate` | Submit batch generation |
| `novel_check_progress` | Check generation progress |
| `novel_resume_all` | Resume all interrupted tasks |
| `novel_full_pipeline` | One-click create complete novel |

### Usage Example

```
User: Create a sci-fi novel "Star Conqueror" with protagonist Jack Chen...

AI: [Calls novel_full_pipeline with characters and outlines]
    ✅ Project created
    ✅ 100 characters created
    ✅ 100 outlines created
    ✅ Batch generation submitted
    
    Your novel is being generated in the background!
```

See [docs/MCP_USAGE_GUIDE.md](docs/MCP_USAGE_GUIDE.md) for detailed documentation.

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI • SQLAlchemy • Pydantic • Alembic |
| **Database** | PostgreSQL 18 • Connection Pool Optimization |
| **Frontend** | React 18 • TypeScript • Ant Design • Zustand |
| **AI** | OpenAI SDK • Gemini SDK • Anthropic SDK |
| **Deployment** | Docker • Docker Compose |

### Project Structure

```
MuMuAINovel/
├── backend/
│   ├── app/
│   │   ├── api/              # 26 API modules
│   │   ├── models/           # 21 data models
│   │   ├── services/         # 31 business services
│   │   └── main.py           # Application entry
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # 25 page components
│   │   └── services/         # API services
│   └── package.json
├── docs/                     # Documentation
│   ├── QUICKSTART.md         # Quick start guide
│   ├── KIRO_INTERACTION_GUIDE.md  # Complete API guide
│   └── NOVEL_CREATION_PIPELINE.md # Pipeline documentation
├── auto_resume.py            # Auto recovery script
├── novel_pipeline.py         # Python automation script
├── docker-compose.yml
└── Dockerfile
```

---

## 📋 Version History

### v1.10.0 (2026-01-05) - Current

**Phase 3 Complete - Advanced Writing Assistance**

| Version | Feature | Description |
|---------|---------|-------------|
| v1.10.0 | Style Guide Integration | Auto-inject learned writing style during AI generation |
| v1.9.0 | Character Growth | Track character ability, relationship, psychology changes |
| v1.8.0 | Duplicate Detection | Detect repetitive content within and across chapters |
| v1.7.0 | Quality Scoring | Basic metrics + AI evaluation, S/A/B/C/D grading |
| v1.6.0 | Style Analysis | Learn project writing style, generate style guides |
| v1.5.0 | Timeline Management | Story event timeline tracking |
| v1.4.0 | Consistency Detection | AI analysis of character behavior and plot coherence |
| v1.3.x | Foreshadowing | Smart tracking, auto-injection during generation |

---

## 🤝 Contributing

Contributions are welcome! Please submit Issues and Pull Requests.

1. Fork this project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Submit Pull Request

---

## 📝 License

This project is licensed under [GNU General Public License v3.0](LICENSE)

- ✅ Free to use, modify, and distribute
- ✅ Can be used for commercial purposes
- 📝 Must open source modified versions
- 📝 Must retain original author copyright

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date)](https://star-history.com/#neosun100/MuMuAINovel)

## 📱 Follow Us

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<div align="center">

**⭐ If this project helps you, please give it a Star!**

Made with ❤️ by Neo

</div>
