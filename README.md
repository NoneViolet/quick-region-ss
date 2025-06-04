# quick-region-ss

## 概要
QuickRegionSSは任意の範囲を簡単にスクリーンショットできるツールです。
Windowsでの動作を保証しています。

## できること
- 任意の影範囲の指定
- 任意のホットキーの指定
- 任意の保存先の指定
- GUIによる操作
- 設定の保存、読込

## 使用方法
### リリースの実行ファイルから実行
1. `QuickRegionSS.exe` を起動
2. 座標設定 ボタンで2点をクリックして撮影範囲を設定
3. フォルダ選択 ボタンで保存先を設定
4. 入力欄に設定したいキーを入力しキー変更ボタンを押下
5. ホットキーを押すと、その範囲のスクリーンショットを自動保存

### ソースコードから実行
```bash
git clone https://github.com/NoneViolet/quick-region-ss.git
cd quick-region-ss
pip install -r requirements.txt
python QuickRegionSS.py
```

## 作成
のーん(紫)