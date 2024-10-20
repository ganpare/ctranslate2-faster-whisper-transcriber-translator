
# ctranslate2-faster-whisper-transcriber&translator

## 概要

このプロジェクトは、音声をリアルタイムで英語に翻訳するツールです。音声の録音からトランスクリプト、そして翻訳までを簡単に操作できます。**PySide6** を使用したGUIインターフェースが提供され、F9キーで録音の開始・停止が可能です。

### 主な機能
- **音声翻訳**: 録音した音声を英語に翻訳します（日本語から英語への翻訳）。
- **ホットキー**: F9キーで録音を開始・停止。
- **二つのテキストウィンドウ**: トランスクリプト結果と翻訳結果をそれぞれ表示します。
- **最新のモデル**: `large-v3` モデルのサポート、翻訳速度の最適化。
- **設定の保存とロード**: `config.yaml` に設定を保存し、起動時に自動ロード。

## インストール手順 (Windows)

### 1. 仮想環境の作成とアクティブ化

1. 仮想環境を作成:
   ```bash
   python3.11 -m venv venv
   ```

2. 仮想環境をアクティブにします:
   ```bash
   .env\Scriptsctivate
   ```

### 2. PyTorch および CUDA の設定

PyTorch 2.4.1 と CUDA 12.1 のサポートを設定します。CUDA対応のPyTorchをインストールするために、以下のコマンドを実行してください。

```bash
pip install torch==2.4.1+cu121 torchaudio==2.4.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

### 3. 依存パッケージのインストール

依存パッケージを `requirements.txt` を使って一括でインストールします。

```bash
pip install -r requirements.txt
```

### 4. メインスクリプトの実行

すべてのパッケージがインストールされた後、メインスクリプトを実行します。

```bash
python ct2_main.py
```

これで、GUIが表示され、F9キーで録音を開始・停止できます。録音終了後、トランスクリプトが表示され、日本語から英語に翻訳されます。

## 設定

`config.yaml` ファイルでモデルやデバイス、量子化オプションを設定できます。デフォルトの設定は以下の通りです。

```yaml
model_name: large-v3
quantization_type: int8_float16
device_type: auto
supported_quantizations:
  cpu: ["int8", "float32", "int8_float32"]
  cuda: ["int8", "float16", "int8_float32", "float32", "int8_float16", "bfloat16", "int8_bfloat16"]
```

設定変更後は、`Update Settings` ボタンをクリックしてモデルを再読み込みしてください。

## 注意点

- **CUDAが有効でない場合**は、自動的にCPUモードに切り替わります。

### `cudnn_ops_infer64_8.dll` エラーに関するTIPS

`Could not locate cudnn_ops_infer64_8.dll` というエラーが発生した場合、以下の手順で対応できます:

1. NVIDIAの公式サイトから、自身の環境に合った cuDNN をダウンロードします: [cuDNN ダウンロードページ](https://developer.download.nvidia.com/compute/cudnn/redist/cudnn/windows-x86_64/)
2. ダウンロードしたファイルを展開し、`bin` ディレクトリをシステムの `PATH` 環境変数に追加します。
   - 例: 私の場合、`cudnn-windows-x86_64-8.9.7.29_cuda12-archive` を使用しました。
   
   展開したフォルダの `bin` ディレクトリのパス（例: `C:\cudnn-windows-x86_64-8.9.7.29_cuda12-archive\bin`）を、Windowsの環境変数に追加することで解決します。

## 元のリポジトリについて

このプロジェクトは、[BBC-Esq/ctranslate2-faster-whisper-transcriber](https://github.com/BBC-Esq/ctranslate2-faster-whisper-transcriber) の派生としてスタートしました。しかし、構成が大幅に変更されたため、独立したリポジトリとして公開しています。オリジナルの貢献者である [BBC-Esq](https://github.com/BBC-Esq) に感謝いたします。

