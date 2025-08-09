# 電子チケットシステム - バックエンド

音楽祭やイベント向けの電子チケット管理システムのFlask製バックエンドAPI

## 概要

このシステムは、イベント参加者が電子チケットを申請・受信し、QRコードでの入場管理を行うためのバックエンドサービスです。PostgreSQLデータベースと連携し、AWS SESやWaypoint APIを使用してメール送信機能を提供します。

## 主な機能

- 🎫 **電子チケット申請システム** - ユーザーがWebフォームから参加申請
- 📧 **自動メール送信** - QRコード付きチケットの自動配信
- 🔍 **QRコード生成・検証** - 入場管理用のユニークなQRコード
- 👥 **ユーザー管理** - 学生・教師・管理者の権限管理
- 📊 **参加者統計** - イベント参加状況の分析
- 🎭 **複数イベント対応** - 異なるイベントでの再利用可能

## システム要件

- Python 3.9+
- PostgreSQL 12+
- Redis (セッション管理用)

## インストール方法

### 1. リポジトリのクローン

```bash
git clone https://github.com/Xiaolin-s-Techclub/E-ticket-backend-flask-public.git
cd E-ticket-backend-flask-public
```

### 2. 仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env.example`を`.env`にコピーして、必要な値を設定してください：

```bash
cp .env.example .env
```

`.env`ファイルを編集して以下の値を設定：

```env
# データベース設定
DB_USER=your_db_username
DB_USER_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=music_fes
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# メール設定
FROM_EMAIL=noreply@yourdomain.com
CONTACT_EMAIL=support@yourdomain.com

# AWS SES設定
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_DEFAULT_REGION=ap-northeast-1

# Waypoint API設定
WAYPOINT_API_UNAME=your_waypoint_username
WAYPOINT_API_PASS=your_waypoint_password

# アプリケーション設定
CUSTOM_HASH_STRING=your_custom_hash_string
SERVER_URL=https://yourdomain.com/
FLASK_SECRET_KEY=your_flask_secret_key_here

# 開発/本番環境の切り替え
DEV_MODE=True  # 本番環境ではFalseに設定
```

### 5. データベースのセットアップ

PostgreSQLサーバーを起動し、データベースを作成：

```sql
CREATE DATABASE music_fes;
```

アプリケーションを起動すると、必要なテーブルが自動作成されます。

### 6. アプリケーションの起動

```bash
python backend/src/app.py
```

開発サーバーは `http://localhost:5000` で起動します。

## API エンドポイント

### チケット申請
- `POST /api/v1/apply` - 新規チケット申請
- `GET /apply/student` - 学生用申請フォーム
- `GET /apply/teacher` - 教師用申請フォーム

### 管理機能
- `GET /admin/dashboard` - 管理者ダッシュボード
- `GET /admin/analytics` - 参加者統計
- `POST /admin/send-tickets` - チケット一括送信

### ユーザー管理
- `POST /api/v1/login` - ユーザーログイン
- `GET /api/v1/users` - ユーザー一覧取得

詳細なAPI仕様は `api-document.yml` を参照してください。

## デプロイ方法

### Heroku
1. Herokuアプリを作成
2. PostgreSQL and Redisアドオンを追加
3. 環境変数を設定
4. `git push heroku main`

### Docker
```bash
docker build -t e-ticket-backend .
docker run -p 5000:5000 --env-file .env e-ticket-backend
```

### DigitalOcean App Platform
`heroku.yml`を参考にApp Specificationを設定してデプロイ

## 開発

### テストの実行
```bash
python -m pytest tests/
```

### データベース接続テスト
```bash
python test_db_conn.py
```

### 開発モードでの起動
```bash
export DEV_MODE=True
python backend/src/app.py
```

## セキュリティについて

このリポジトリは公開用にセキュリティクリーンアップが実施済みです：

- 🔒 すべての認証情報を環境変数に移行
- 🚫 `.env`ファイルと認証情報ディレクトリを削除
- 📝 包括的な`.gitignore`で今後の情報漏洩を防止
- 🔐 Flask秘密鍵をハードコードから環境変数に変更
- 📚 設定例として`.env.example`を提供

詳細は `SECURITY_CLEANUP.md` を参照してください。

## ファイル構成

```
├── backend/
│   ├── src/
│   │   ├── config/         # 設定ファイル
│   │   ├── model/          # データモデル
│   │   ├── service/        # ビジネスロジック
│   │   ├── api.py          # APIエンドポイント
│   │   └── app.py          # メインアプリケーション
│   ├── outputs/            # 生成されるチケット画像
│   └── references/         # チケットテンプレート
├── frontend/
│   ├── templates/          # HTMLテンプレート
│   └── static/            # CSS、JavaScript
├── .env.example           # 環境変数のテンプレート
├── requirements.txt       # Python依存関係
└── api-document.yml       # API仕様書
```

## 貢献方法

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## サポート

質問やバグ報告は [Issues](https://github.com/Xiaolin-s-Techclub/E-ticket-backend-flask-public/issues) でお願いします。

---

**開発チーム**: Xiaolin's TechClub  
**連絡先**: xiaolinstechclub@gmail.com