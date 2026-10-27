# MotionBuilderTools

MotionBuilder (pyfbsdk) 用の自作スクリプト集です。
メニューバーからワンクリックで呼び出せるランチャー付き。

## 含まれるツール

| メニュー | ファイル | 内容 |
|---|---|---|
| Tpose | `1_Tpose/Tpose.py` | Hipsのグローバル回転Yを0にし、ショルダー以降（腕・手・指）の回転を0にしてTポーズに近づける |
| Characterize | `2_Characterize/Characterize.py` | スケルトンを検出し、名前を確認しながら FBCharacter を自動作成（複数キャラ対応） |
| Camera | `3_Camera/CameraandRight.py` | 固定カメラ（Front/Side/Perspective）、キャラ追従カメラ、ライト4灯を追加するUIツール |

## フォルダ構成

```
MotionBuilderTools/
├── seisakuScriput_launcher.py   ← ランチャー（メニュー作成）
└── seisakuScriput/
    ├── 1_Tpose/
    │   └── Tpose.py
    ├── 2_Characterize/
    │   └── Characterize.py
    └── 3_Camera/
        └── CameraandRight.py
```

## インストール

1. このリポジトリをダウンロード（`Code` → `Download ZIP`）または `git clone`
2. `seisakuScriput_launcher.py` と `seisakuScriput` フォルダを、同じ場所に置いたまま MotionBuilder の起動スクリプトフォルダへコピー

   例（バージョンは環境に合わせてください）:
   - Windows: `C:\Users\<ユーザー名>\Documents\MB\<バージョン>\config\PythonStartup\`
   - または MotionBuilder の `bin\config\PythonStartup\`

3. MotionBuilder を再起動すると、メニューバーの **Help の右** に `seisakuScriput` が表示されます

> ランチャーを使わず、各スクリプトを `Python Editor` で開いて直接実行することも可能です。

## 使い方の流れ

```
Tpose → Characterize → Camera
(姿勢を整える) (キャラクタライズ) (カメラ・ライト配置)
```

## スクリプトの追加方法

`seisakuScriput` 内のフォルダに `.py` を置くだけで、次回起動時にメニューへ追加されます。

- フォルダ名の先頭の番号（`1_` など）は並び順用で、メニューには表示されません
- 新しいカテゴリを作るときは `4_Xxx` のようにフォルダを作成してください
- 1フォルダにつき最大99個のスクリプトまで対応

## 注意点

- `Characterize.py` はボーンを名前の部分一致で検索します。`Spine1` などを含むリグでは、意図しないボーンが割り当てられる場合があります
- `Tpose.py` は、リグのボーン軸の向きによってはきれいなTポーズにならない場合があります

## ライセンス

MIT License（`LICENSE` 参照）
