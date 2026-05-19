import argparse
import os
import sys
from PIL import Image
from rembg import remove

def main():
    # コマンドライン引数の定義
    parser = argparse.ArgumentParser(
        description="人物写真の背景を除去します。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-i", "--input", required=True, help="入力画像のパス")
    parser.add_argument("-o", "--output", required=True, help="出力画像のパス")
    parser.add_argument("--white-bg", action="store_true", 
                        help="背景を白く設定する（未指定時は透明背景）")

    args = parser.parse_args()

    try:
        # 1. 画像読み込み＆背景除去（内部でU2-Netモデルが使用される）
        input_img = Image.open(args.input).convert("RGBA")
        no_bg_img = remove(input_img)

        # 2. 白背景の設定処理
        if args.white_bg:
            # アルファチャンネルをマスクとして使い、白キャンバスに貼り付け
            white_bg = Image.new("RGB", no_bg_img.size, (255, 255, 255))
            white_bg.paste(no_bg_img, mask=no_bg_img.split()[3])
            final_img = white_bg
        else:
            final_img = no_bg_img

        # 3. 保存時の形式チェック
        ext = os.path.splitext(args.output)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            print("⚠️ 注意: .jpg/.jpegは透明度をサポートしません。白背景に変換して保存します。")
            final_img.convert("RGB").save(args.output, quality=95)
        else:
            final_img.save(args.output)

        print(f"✅ 完了: '{args.output}' に保存しました。")

    except FileNotFoundError:
        print(f"❌ エラー: ファイル '{args.input}' が見つかりません。")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラー: 処理中に問題が発生しました。\n{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
