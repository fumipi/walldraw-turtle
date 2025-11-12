[English version → README_en.md](./README_en.md)
# 🐢かめプロッター

Raspberry Pi Pico と MicroPython で作る最小構成の亀の形をした垂直型ペンプロッターです。  
CSVファイルに基づいて線画を描きます。

---

## プロジェクト概要

### **ハードウェア & ファームウェア ** 
- タートルグラフィックス風の MicroPython 制御コード  
- **Raspberry Pi Pico**, **28BYJ-48 ステッピングモータ ×2**, **SG90 サーボモータ ×1** を使用  
- 電源は USB から給電 
- **3Dプリント部品（STL）**、**回路図**、**サンプル CSV**   


## 使い方

### **タートルプロッターのセットアップ**
1. STLフォルダの亀パーツを3Dプリントする
2. Schematicフォルダにある回路図を参考に配線する
3. [Thonny IDE](https://thonny.org/) をインストール  
4. Raspberry Pi Pico を USB で PC に接続、MicroPythonをインストール [参考](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
5. Codeフォルダにあるコードを全てPicoにDrag & Drop
6. `turtle_plotter/code/main.py` を Thonny で開いて実行  
5. `points.csv` を Pico にアップロード（省略可）

**動作モード**
- `points.csv` がある場合 → CSV 座標を描画  
- ない場合 → `main.py` 内の `test_drawing` に従って 100mm 四方のテスト描画  

---

### 線描データ作成アプリ
[https://vectorizer.streamlit.app/](https://vectorizer.streamlit.app/) にアクセスし、画像や をアップロード。  
生成された CSV をダウンロードして `points.csv` として Pico に保存します。
**主な機能**
- 輪郭抽出・センターライン抽出  
- 経路の最適化と単純化  
- 画像 → CSV変換  （このプロッターでは使いませんが、SVGやGコードへの変換もできます）

## より詳しい作り方
[note](https://note.com/fumi_note/n/n50b205639b7f)をご覧ください。

## 参考プロジェクト
- 参考: [Make a Raspberry Pi Pico pen plotter](https://www.raspberrypi.com/news/make-a-raspberry-pi-pico-pen-plotter/)


