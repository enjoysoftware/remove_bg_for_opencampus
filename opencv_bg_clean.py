import cv2
import mediapipe as mp
import numpy as np

# MediaPipeのSelfie Segmentation（背景分離）の準備
mp_selfie_segmentation = mp.solutions.selfie_segmentation
# model_selection=0 は一般用（1は景色の変化に強いが少し重い）
selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=0)

# Webカメラのキャプチャを開始 (0は内蔵カメラ、外付けの場合は1などを指定)
cap = cv2.VideoCapture(2)

print("プログラムを終了するには 'q' キーを押してください。")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("カメラからの映像を取得できませんでした。")
        break

    # OpenCVはBGR形式なので、MediaPipe用にRGB形式に変換
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # セグメンテーション（人物の検出）を実行
    results = selfie_segmentation.process(frame_rgb)
    
    # 検出結果のマスクを取得 (0.0〜1.0の確率マップ)
    mask = results.segmentation_mask
    
    # 境界をはっきりさせるため、閾値を設定して2値化（0 or 1）
    # 0.5以上の確率で人物である部分を1（True）とする
    condition = mask > 0.5
    
    # 3チャンネル（BGR）に拡張
    condition = np.stack((condition,) * 3, axis=-1)
    
    # 背景用：カメラ画像と同じサイズで「真っ白（255）」の画像を作成
    white_background = np.ones(frame.shape, dtype=np.uint8) * 255
    
    # 条件（condition）がTrueなら元のカメラ画像（frame）、Falseなら白背景を採用
    output_frame = np.where(condition, frame, white_background)
    
    # 結果をウィンドウに表示
    cv2.imshow('Real-time Background Replacement', output_frame)
    
    # 'q' キーが押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 後片付け
cap.release()
cv2.destroyAllWindows()
selfie_segmentation.close()