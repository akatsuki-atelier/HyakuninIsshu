# 百人一首 読み上げアプリ

VOICEVOX で生成した音声ファイルを使って百人一首を読み上げるWebアプリです。

## 機能

- 100首から読み上げる歌を選択
- 上の句を読み上げ → 1.5秒後に下の句を読み上げ
- 読み上げ速度の調整
- 作者・歌での検索・絞り込み
- 選択状態を次回起動時に復元

## 使い方

1. `index.html` をブラウザで開く
2. 読み上げたい歌にチェックを入れる
3. 「読み上げ開始」ボタンを押す

## 音声ファイルの生成

音声ファイルは [VOICEVOX](https://voicevox.hiroshiba.jp/) を使って生成します。

### 必要なもの

- VOICEVOX（起動しておく）
- Python 3
- ffmpeg（`brew install ffmpeg`）

### 手順

```bash
pip3 install requests
python3 generate_audio.py
```

`audio/` フォルダに200ファイル（`001_kami.mp3` 〜 `100_shimo.mp3`）が生成されます。

生成済みファイルをスキップして再実行する場合：

```bash
python3 generate_audio.py --skip-existing
```

## ファイル構成

```
index.html          # メインアプリ
generate_audio.py   # 音声生成スクリプト
audio/
  001_kami.mp3      # 1番歌・上の句
  001_shimo.mp3     # 1番歌・下の句
  ...
  100_kami.mp3
  100_shimo.mp3
```
