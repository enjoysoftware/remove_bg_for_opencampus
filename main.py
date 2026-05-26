from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import shutil
import io
from PIL import Image
from rembg import remove
from datetime import datetime
from typing import Optional

app = FastAPI()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 画像を保存するディレクトリ
SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)

def process_image_background(input_bytes: bytes, white_bg: bool = False) -> Image.Image:
    """画像を処理してPIL Imageオブジェクトを返す共通ロジック"""
    input_img = Image.open(io.BytesIO(input_bytes)).convert("RGBA")
    no_bg_img = remove(input_img)
    
    if white_bg:
        white_bg_layer = Image.new("RGB", no_bg_img.size, (255, 255, 255))
        white_bg_layer.paste(no_bg_img, mask=no_bg_img.split()[3])
        return white_bg_layer
    return no_bg_img

@app.post("/api/white-bg")
async def white_bg_endpoint(file: UploadFile = File(...)):
    """背景を白く加工してプレビュー画像を返すエンドポイント"""
    try:
        contents = await file.read()
        final_img = process_image_background(contents, white_bg=True)
        
        img_byte_arr = io.BytesIO()
        final_img.convert("RGB").save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/upload-face")
async def upload_face(
    face_image: UploadFile = File(...), 
    white_bg: Optional[bool] = Form(False)
):
    """
    画像を保存するエンドポイント。
    white_bgがTrueの場合、保存前に背景を白く加工する。
    """
    try:
        contents = await face_image.read()
        
        if white_bg:
            # 背景白色化が必要な場合
            processed_img = process_image_background(contents, white_bg=True)
            img_byte_arr = io.BytesIO()
            processed_img.convert("RGB").save(img_byte_arr, format='JPEG', quality=95)
            save_contents = img_byte_arr.getvalue()
        else:
            # そのまま保存する場合
            save_contents = contents

        # ファイル名の生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{face_image.filename}"
        if white_bg and not filename.lower().endswith(".jpg"):
            filename = os.path.splitext(filename)[0] + ".jpg"
            
        file_path = os.path.join(SAVE_DIR, filename)
        
        # 保存
        with open(file_path, "wb") as f:
            f.write(save_contents)
            
        print(f"[保存完了] {file_path} (Background Whitened: {white_bg})")
        return {
            "status": "success", 
            "filename": filename,
            "processed": white_bg
        }
    except Exception as e:
        print(f"[保存エラー] {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print("Signage Combined API Server を起動します (http://localhost:3000)")
    uvicorn.run(app, host="0.0.0.0", port=3000)
