# 勤怠管理ツール（Attendance Management Tool）

## 📋 概要
このツールは、従業員の勤怠データを効率的に管理・分析するためのPythonベースの管理システムです。
Excelファイルを介して勤怠データの入出力を行い、労働時間の計算や集計レポートの作成を自動化します。

## ✨ 主な機能
- 勤怠データのExcelファイルからの一括インポート
- 勤務時間の自動計算（残業時間、深夜勤務時間を含む）
- 部署別・個人別の勤怠集計
- 月次レポートの自動生成
- データの検証と異常値検出
- 集計結果のExcelエクスポート

## 🔧 技術要件
- Python 3.8以上
- Poetry（パッケージ管理）

### 必要なパッケージ
```toml
[tool.poetry.dependencies]
python = "^3.8"
pandas = "^2.0.0"
openpyxl = "^3.1.0"
numpy = "^1.24.0"
pytest = "^7.3.1"
```

## 🚀 セットアップ
1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/attendance-management.git
cd attendance-management
```

2. Poetry環境のセットアップ
```bash
poetry install
```

3. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な設定を行う
```

## 💻 使用方法

### 基本的な使用方法
```bash
# 仮想環境の有効化
poetry shell

# プログラムの実行
python -m src.main

# 特定の月のデータを処理する場合
python -m src.main --month 2024-01
```

### データファイルの配置
1. `data/input` ディレクトリに入力用Excelファイルを配置
2. ファイル名は `YYYYMM_attendance.xlsx` の形式で保存
3. 処理結果は `data/output` ディレクトリに出力

## 📁 プロジェクト構造
```
attendance-management/
├── src/
│   ├── __init__.py
│   ├── main.py              # メインスクリプト
│   ├── config/             # 設定ファイル
│   ├── models/             # データモデル
│   ├── services/           # ビジネスロジック
│   └── utils/              # ユーティリティ関数
├── tests/                  # テストコード
├── data/
│   ├── input/             # 入力データ
│   └── output/            # 出力データ
├── docs/                  # ドキュメント
├── poetry.lock
├── pyproject.toml
└── README.md
```

## 🧪 テスト
```bash
# 全てのテストを実行
poetry run pytest

# カバレッジレポートの生成
poetry run pytest --cov=src tests/
```

## 📝 コントリビューション
1. このリポジトリをフォーク
2. 新しいブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m '✨ feat: 素晴らしい機能を追加'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 🔒 セキュリティ
- 個人情報を含むデータは暗号化して保存
- アクセスログの記録
- 定期的なバックアップの実施

## 📄 ライセンス
MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 👥 サポート
問題や質問がある場合は、Issueを作成してください。 