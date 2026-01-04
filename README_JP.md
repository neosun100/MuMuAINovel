[English](README.md) | [简体中文](README_CN.md) | [繁體中文](README_TW.md) | [日本語](README_JP.md)

<div align="center">

# MuMuAINovel 📚✨

**🚀 AI駆動の小説執筆アシスタント | 100万字以上の長編小説を自動生成**

![Version](https://img.shields.io/badge/version-1.10.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)
![React](https://img.shields.io/badge/react-18.3.1-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-blue.svg)
![License](https://img.shields.io/badge/license-GPL%20v3-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![API](https://img.shields.io/badge/API%20Endpoints-200+-orange.svg)

**⭐ このプロジェクトが役に立ったら、Starをお願いします！**

</div>

---

## 🎯 主な特徴

| 機能 | 説明 |
|------|------|
| 🤖 **マルチAI対応** | OpenAI / Gemini / Claude シームレス切り替え |
| 📖 **スマート章生成** | RTCOフレームワークによる動的コンテキスト、自動プロット継続 |
| 🎭 **キャラクター管理** | 関係図、組織図、成長追跡 |
| 🔮 **伏線システム** | スマート追跡、生成時自動注入 |
| 📊 **品質スコアリング** | 基本指標 + AI評価、S/A/B/C/Dグレード |
| 🔍 **一貫性チェック** | AIによるキャラクター行動とプロット整合性分析 |
| ⏱️ **タイムライン管理** | ストーリーイベントのタイムライン追跡と可視化 |
| 🎨 **スタイル分析** | 執筆スタイルを学習、スタイルガイド生成 |
| 🔄 **重複検出** | 章内および章間の重複コンテンツ検出 |
| 💾 **PostgreSQL** | 本番グレードDB、200+同時ユーザー対応 |
| 🚀 **バッチ生成** | 100章×10,000字を自動生成 |

---

## ✨ 機能

### コア機能

- 🤖 **マルチAIモデル** - OpenAI、Gemini、Claude、カスタムAPIエンドポイント対応
- 📝 **スマートウィザード** - AIがアウトライン、キャラクター、世界観を自動生成
- 👥 **キャラクター管理** - ビジュアル関係図と組織管理
- 📖 **章エディター** - 章の作成、編集、再生成、推敲
- 🌐 **世界構築** - 完全なストーリー背景構築
- 💡 **インスピレーションモード** - AI駆動のクリエイティブアイデア生成
- ✍️ **カスタムスタイル** - カスタムAI執筆スタイル対応
- 📊 **マインドマップ** - 章のロジック関係を可視化

### 高度な機能 (v1.3.0+)

- 🔮 **伏線管理** - プロット伏線の追跡、未解決スレッドのリマインド
- 🔍 **一貫性検出** - AIによるキャラクター行動とプロット整合性分析
- ⏱️ **タイムライン管理** - ストーリーイベントのタイムライン追跡
- 🎨 **スタイル分析** - プロジェクトの執筆スタイルを学習、スタイルガイド生成
- 📊 **章品質スコアリング** - 基本指標 + AI総合評価
- 🔄 **重複検出** - 重複/類似コンテンツの検出
- 📈 **キャラクター成長** - キャラクターの能力、関係、心理変化を追跡

---

## 🚀 クイックスタート

### 前提条件

- Docker と Docker Compose
- 少なくとも1つのAIサービスAPIキー（OpenAI/Gemini/Claude）

### Docker Compose デプロイ（推奨）

```bash
# 1. プロジェクトをクローン
git clone https://github.com/neosun100/MuMuAINovel.git
cd MuMuAINovel

# 2. 環境変数を設定
cp .env.example .env
# .envファイルを編集し、APIキーとデータベースパスワードを入力

# 3. サービスを起動
docker-compose up -d

# 4. アプリケーションにアクセス
# ブラウザで http://localhost:8000 を開く
```

### Docker Hub イメージを使用

```bash
# 最新イメージをプル（モデルファイル含む）
docker pull mumujie/mumuainovel:latest

# 設定して起動
cp .env.example .env
docker-compose up -d
```

---

## ⚙️ 設定

### 必須設定 (.env)

```bash
# PostgreSQL データベース
DATABASE_URL=postgresql+asyncpg://mumuai:your_password@postgres:5432/mumuai_novel
POSTGRES_PASSWORD=your_secure_password

# AIサービス（少なくとも1つ設定）
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.openai.com/v1
DEFAULT_AI_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini

# ローカルアカウントログイン
LOCAL_AUTH_ENABLED=true
LOCAL_AUTH_USERNAME=admin
LOCAL_AUTH_PASSWORD=your_password
```

### オプション設定

```bash
# LinuxDO OAuth
LINUXDO_CLIENT_ID=your_client_id
LINUXDO_CLIENT_SECRET=your_client_secret

# Gemini
GEMINI_API_KEY=your_gemini_key

# Claude
ANTHROPIC_API_KEY=your_anthropic_key

# コネクションプール（高同時接続）
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=30
```

---

## 📚 APIドキュメント

### API概要

このプロジェクトは、小説作成ワークフロー全体をカバーする **200以上のRESTful APIエンドポイント** を提供します。

| モジュール | エンドポイント数 | 説明 |
|------------|------------------|------|
| Auth | 8 | ログイン、OAuth、セッション管理 |
| Projects | 12 | プロジェクトCRUD、インポート/エクスポート |
| Outlines | 15 | アウトライン生成、編集、AI継続 |
| Characters | 18 | キャラクター管理、関係図 |
| Chapters | 25 | 章生成、編集、バッチ操作 |
| Foreshadows | 10 | 伏線追跡、解決リマインダー |
| Consistency | 4 | キャラクター/プロット一貫性検出 |
| Timeline | 6 | イベントタイムライン管理 |
| Style | 3 | 執筆スタイル学習と分析 |
| Quality | 2 | 章品質評価 |
| Duplicate | 2 | 重複コンテンツ検出 |
| Growth | 6 | キャラクター成長追跡 |

### オンラインドキュメント

サービス起動後にアクセス：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 小説作成パイプライン

### 自動化ワークフロー

MuMuAINovelはAPIを通じた完全自動小説作成をサポート：

```
1. POST /api/auth/local/login           # ログイン
2. POST /api/projects                    # プロジェクト作成
3. PUT  /api/projects/{id}               # 世界観設定
4. POST /api/characters (ループ)         # キャラクター作成 (80-150)
5. POST /api/outlines (ループ)           # アウトライン作成 (100章)
6. POST /api/chapters (ループ)           # 章作成 (100)
7. POST /api/chapters/project/{id}/batch-generate  # バッチ生成送信
8. GET  /api/chapters/project/{id}       # 進捗監視
```

### 主要パラメータ

| パラメータ | デフォルト | 範囲 | 説明 |
|------------|------------|------|------|
| count | 10 | 1-100 | 生成章数 |
| target_word_count | 10000 | 1000-20000 | 章あたりの文字数 |
| max_retries | 10 | 0-20 | 最大リトライ回数 |

### RTCO コンテキストフレームワーク

```
章番号      コンテキスト戦略
─────────────────────────────────
第1章       アウトライン + キャラクターのみ
第2-10章    前章末尾300字 + 関連キャラクター
第11-50章   前章末尾500字 + 関連メモリ3件
第51章+     前章末尾500字 + ストーリー骨格 + スマートメモリ5件
```

### リトライ戦略（段階的バックオフ）

| リトライ回数 | 待機時間 | 説明 |
|--------------|----------|------|
| 1-3 | 2, 4, 8秒 | クイックリトライ |
| 4-6 | 30秒 | 中程度の待機 |
| 7-10 | 60秒 | 長い待機 |

---

## 🔄 タスク復旧

### 自動復旧スクリプト

```bash
# 一回限りの復旧
python auto_resume.py

# デーモンモード（全完了まで）
python auto_resume.py --daemon

# バックグラウンドでログ記録
nohup python auto_resume.py --daemon > resume.log 2>&1 &
```

### 環境変数

```bash
export MUMUAI_BASE_URL=http://localhost:8000
export MUMUAI_USERNAME=admin
export MUMUAI_PASSWORD=your_password
```

---

## 🏗️ 技術スタック

| レイヤー | 技術 |
|----------|------|
| **バックエンド** | FastAPI • SQLAlchemy • Pydantic • Alembic |
| **データベース** | PostgreSQL 18 • コネクションプール最適化 |
| **フロントエンド** | React 18 • TypeScript • Ant Design • Zustand |
| **AI** | OpenAI SDK • Gemini SDK • Anthropic SDK |
| **デプロイ** | Docker • Docker Compose |

### プロジェクト構造

```
MuMuAINovel/
├── backend/
│   ├── app/
│   │   ├── api/              # 26 APIモジュール
│   │   ├── models/           # 21 データモデル
│   │   ├── services/         # 31 ビジネスサービス
│   │   └── main.py           # アプリケーションエントリ
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/            # 25 ページコンポーネント
│   │   └── services/         # APIサービス
│   └── package.json
├── docs/                     # ドキュメント
│   ├── QUICKSTART.md         # クイックスタートガイド
│   ├── KIRO_INTERACTION_GUIDE.md  # 完全APIガイド
│   └── NOVEL_CREATION_PIPELINE.md # パイプラインドキュメント
├── auto_resume.py            # 自動復旧スクリプト
├── novel_pipeline.py         # Python自動化スクリプト
├── docker-compose.yml
└── Dockerfile
```

---

## 📋 バージョン履歴

### v1.10.0 (2026-01-05) - 現在

**フェーズ3完了 - 高度な執筆支援**

| バージョン | 機能 | 説明 |
|------------|------|------|
| v1.10.0 | スタイルガイド統合 | AI生成時に学習した執筆スタイルを自動注入 |
| v1.9.0 | キャラクター成長 | キャラクターの能力、関係、心理変化を追跡 |
| v1.8.0 | 重複検出 | 章内および章間の重複コンテンツ検出 |
| v1.7.0 | 品質スコアリング | 基本指標 + AI評価、S/A/B/C/Dグレード |
| v1.6.0 | スタイル分析 | プロジェクトの執筆スタイルを学習、スタイルガイド生成 |
| v1.5.0 | タイムライン管理 | ストーリーイベントのタイムライン追跡 |
| v1.4.0 | 一貫性検出 | AIによるキャラクター行動とプロット整合性分析 |
| v1.3.x | 伏線システム | スマート追跡、生成時自動注入 |

---

## 🤝 コントリビューション

コントリビューション歓迎！Issues と Pull Requests をお待ちしています。

1. このプロジェクトをFork
2. 機能ブランチを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. ブランチにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Request を送信

---

## 📝 ライセンス

このプロジェクトは [GNU General Public License v3.0](LICENSE) でライセンスされています

- ✅ 自由に使用、修正、配布可能
- ✅ 商用利用可能
- 📝 修正版はオープンソースにする必要あり
- 📝 原作者の著作権を保持する必要あり

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=neosun100/MuMuAINovel&type=Date)](https://star-history.com/#neosun100/MuMuAINovel)

## 📱 フォローする

![WeChat](https://img.aws.xin/uPic/扫码_搜索联合传播样式-标准色版.png)

---

<div align="center">

**⭐ このプロジェクトが役に立ったら、Starをお願いします！**

Made with ❤️ by Neo

</div>
