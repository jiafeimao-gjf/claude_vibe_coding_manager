# Claude History Manager

[English](#english) · [简体中文](#简体中文) · [日本語](#日本語) · [한국어](#한국어) · [Français](#français) · [Español](#español) · [Deutsch](#deutsch)

---

## English

A Claude conversation history management system that imports data from the local `~/.claude` directory into a local SQLite database and provides a Vue 3 web UI to browse, search, and resume sessions.

### Features

- **Full & incremental import** of `~/.claude` data (history.jsonl, sessions/, projects/, file-history/)
- **Project, session, message browser** with search and filters
- **File history viewer** for versioned file snapshots
- **Dashboard** with activity timeline, top projects, and recent sessions
- **Continue session** — generate a one-click `claude --resume <session_id>` command from any session
- **Dark mode** with `localStorage` persistence
- **i18n** — Chinese / English toggle, date formatting follows the active locale
- **Pure local** — SQLite file in `data/`, no external services required

### Tech Stack

| Layer | Stack |
|---|---|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| Backend | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| Test | pytest (15 tests, all passing) |

### Ports

- Backend: `http://localhost:9453`
- Frontend: `http://localhost:8453`

### Run

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9453

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

Open <http://localhost:8453>, click **Import** → **Full Import** to load data.

### API

- `POST /api/import/full` — re-import everything
- `POST /api/import/incremental` — import new entries only
- `GET /api/projects` · `GET /api/projects/{id}`
- `GET /api/sessions` · `GET /api/sessions/{id}`
- `GET /api/messages/search?q=`
- `GET /api/file-history` · `GET /api/file-history/{id}`
- `GET /api/stats/overview` · `GET /api/stats/timeline`

Full API docs at <http://localhost:9453/docs>.

### License

MIT — see [LICENSE](./LICENSE).

---

## 简体中文

Claude 对话历史管理系统：将本地 `~/.claude` 目录中的数据导入到本地 SQLite 数据库，通过 Vue 3 Web 界面浏览、搜索和恢复会话。

### 功能

- **全量 / 增量导入** `~/.claude` 数据（history.jsonl、sessions/、projects/、file-history/）
- **项目 / 会话 / 消息浏览** 与搜索过滤
- **文件历史** 版本快照查看
- **总览面板** 活动趋势、热门项目、最近会话
- **继续开发** 一键生成 `claude --resume <session_id>` 命令
- **黑夜模式** 通过 `localStorage` 持久化
- **国际化** 中英文切换，日期格式跟随当前语言
- **完全本地** SQLite 文件存于 `data/`，无需外部服务

### 技术栈

| 层 | 栈 |
|---|---|
| 前端 | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide 图标 |
| 后端 | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| 测试 | pytest（15 个测试全部通过） |

### 端口

- 后端：`http://localhost:9453`
- 前端：`http://localhost:8453`

### 运行

```bash
# 后端
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9453

# 前端（新终端）
cd frontend
npm install
npm run dev
```

打开 <http://localhost:8453>，点击 **导入** → **全量导入** 加载数据。

### API

- `POST /api/import/full` — 全量重新导入
- `POST /api/import/incremental` — 仅导入新条目
- `GET /api/projects` · `GET /api/projects/{id}`
- `GET /api/sessions` · `GET /api/sessions/{id}`
- `GET /api/messages/search?q=`
- `GET /api/file-history` · `GET /api/file-history/{id}`
- `GET /api/stats/overview` · `GET /api/stats/timeline`

完整 API 文档：<http://localhost:9453/docs>。

### 许可

MIT — 见 [LICENSE](./LICENSE)。

---

## 日本語

`~/.claude` ローカルディレクトリのデータを SQLite に取り込み、Vue 3 Web UI で閲覧・検索・再開できる、Claude 会話履歴管理システム。

### 特徴

- `~/.claude` データの **全量 / 増分インポート**
- プロジェクト・セッション・メッセージの **ブラウジングと検索**
- ファイルスナップショットの **履歴ビューア**
- アクティビティタイムライン、TOP プロジェクト、最近のセッションを表示する **ダッシュボード**
- 任意セッションから **`claude --resume <session_id>` コマンドをワンクリック生成**
- `localStorage` に永続化される **ダークモード**
- **i18n** 簡体中文 / 英語切替、日付フォーマットも追従
- **完全ローカル** SQLite ファイルは `data/` 配下、外部サービス不要

### 技術スタック

| 層 | スタック |
|---|---|
| フロントエンド | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| バックエンド | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| テスト | pytest（15 件すべて成功） |

### ポート

- バックエンド：`http://localhost:9453`
- フロントエンド：`http://localhost:8453`

---

## 한국어

로컬 `~/.claude` 디렉터리의 데이터를 SQLite 로 가져와 Vue 3 웹 UI 로 검색·열람·재개할 수 있는 Claude 대화 기록 관리 시스템.

### 기능

- `~/.claude` 데이터의 **전체 / 증분 가져오기**
- 프로젝트·세션·메시지 **검색 및 열람**
- 파일 스냅샷의 **기록 뷰어**
- 활동 타임라인·인기 프로젝트·최근 세션을 보여주는 **대시보드**
- 임의 세션에서 **`claude --resume <session_id>` 명령어를 원클릭 생성**
- `localStorage` 에 저장되는 **다크 모드**
- **i18n** 중국어 / 영어 토글, 날짜 형식도 자동 적용
- **완전 로컬** SQLite 파일이 `data/` 에 저장되며 외부 서비스 불필요

### 기술 스택

| 계층 | 스택 |
|---|---|
| 프런트엔드 | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| 백엔드 | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| 테스트 | pytest (15개 테스트 모두 통과) |

### 포트

- 백엔드: `http://localhost:9453`
- 프런트엔드: `http://localhost:8453`

---

## Français

Un système de gestion de l'historique des conversations Claude qui importe les données du dossier local `~/.claude` dans une base SQLite locale, puis offre une interface web Vue 3 pour parcourir, rechercher et reprendre des sessions.

### Fonctionnalités

- **Importation complète & incrémentale** des données `~/.claude`
- **Navigation projets / sessions / messages** avec recherche et filtres
- **Historique des fichiers** versionnés
- **Tableau de bord** chronologie d'activité, projets principaux, sessions récentes
- **Reprendre une session** — commande `claude --resume <session_id>` en un clic
- **Mode sombre** persistant via `localStorage`
- **i18n** chinois / anglais, formats de date adaptés
- **100% local** — fichier SQLite dans `data/`, aucun service externe requis

### Stack

| Couche | Stack |
|---|---|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| Backend | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| Tests | pytest (15 tests, tous OK) |

### Ports

- Backend : `http://localhost:9453`
- Frontend : `http://localhost:8453`

---

## Español

Un sistema de gestión del historial de conversaciones de Claude que importa datos del directorio local `~/.claude` a una base SQLite local y proporciona una UI web Vue 3 para navegar, buscar y reanudar sesiones.

### Características

- **Importación completa e incremental** de datos `~/.claude`
- **Explorador de proyectos, sesiones y mensajes** con búsqueda y filtros
- **Visor de historial de archivos** versionados
- **Panel** con línea de tiempo de actividad, proyectos principales y sesiones recientes
- **Continuar sesión** — comando `claude --resume <session_id>` con un solo clic
- **Modo oscuro** persistente en `localStorage`
- **i18n** chino / inglés, formatos de fecha adaptados
- **Totalmente local** — archivo SQLite en `data/`, sin servicios externos

### Stack

| Capa | Stack |
|---|---|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| Backend | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| Tests | pytest (15 tests, todos OK) |

### Puertos

- Backend: `http://localhost:9453`
- Frontend: `http://localhost:8453`

---

## Deutsch

Ein Verwaltungssystem für den Claude-Konversationsverlauf, das Daten aus dem lokalen `~/.claude`-Verzeichnis in eine lokale SQLite-Datenbank importiert und über eine Vue-3-Weboberfläche das Durchsuchen, Filtern und Fortsetzen von Sitzungen ermöglicht.

### Funktionen

- **Vollständiger & inkrementeller Import** der `~/.claude`-Daten
- **Projekt-, Sitzungs- und Nachrichten-Browser** mit Suche und Filtern
- **Dateihistorie** versionierter Snapshots
- **Dashboard** mit Aktivitäts-Zeitachse, Top-Projekten und letzten Sitzungen
- **Sitzung fortsetzen** — `claude --resume <session_id>`-Befehl mit einem Klick
- **Dunkelmodus** mit `localStorage`-Persistenz
- **i18n** Chinesisch / Englisch, Datumsformate folgen der Sprache
- **Vollständig lokal** — SQLite-Datei in `data/`, keine externen Dienste erforderlich

### Stack

| Schicht | Stack |
|---|---|
| Frontend | Vue 3 + Vite + Pinia + Vue Router + TailwindCSS v4 + vue-i18n + Lucide Icons |
| Backend | Python 3.11+ + FastAPI + SQLAlchemy 2 + SQLite |
| Tests | pytest (15 Tests, alle bestanden) |

### Ports

- Backend: `http://localhost:9453`
- Frontend: `http://localhost:8453`

### Lizenz

MIT — siehe [LICENSE](./LICENSE).
