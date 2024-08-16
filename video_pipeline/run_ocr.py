import copy
import glob
import json
from multiprocessing import Pool

import cv2
import os

from tqdm import tqdm

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from paddleocr import PaddleOCR
# Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)  # need to run only once to download and load model into memory


def run_ocr_for_video():
    input_samples = []
    skip_set = set()
    if os.path.exists("../.cache/ocr_results.jsonl"):
        with open("../.cache/ocr_results.jsonl", "r", encoding="utf-8") as f:
            for l in f:
                s = json.loads(l)
                del s["ocr"]
                skip_set.add(str(s))
    
    with open("../.cache/framefiles.jsonl", "r", encoding="utf-8") as f:
        for l in f:
            sample = json.loads(l)
            for frame in sample["frames"]:
                input_sample = {"video": sample["video"], "frame": frame}
                if str(input_sample) in skip_set:
                    continue
                input_samples.append(input_sample)

    with open("../.cache/ocr_results.jsonl", "a+", encoding="utf-8") as f:
        # for s in tqdm(input_samples):
        #     s["ocr"] = run_ocr_for_img(s["frame"])
        #     print(json.dumps(s, ensure_ascii=False), file=f)

        # batch
        batches, batch = [], []
        for s in input_samples:
            batch.append(s)
            if len(batch) >= 1000:
                batches.append(batch)
                batch = []
        if len(batch):
            batches.append(batch)
        for batch in tqdm(batches):
            pool = Pool(6)
            for j, res in enumerate(pool.map(run_ocr_for_img, tqdm([b["frame"] for b in batch]))):
                batch[j]["ocr"] = res
                print(json.dumps(batch[j], ensure_ascii=False), file=f)


def run_ocr_for_img(img_path: str):
    if not os.path.exists(img_path):
        return []
    result = []
    for res in ocr.ocr(img_path, cls=True):
        if res:
            for line in res:
                result.append({"box": line[0], "text": line[1][0], "score": line[1][1]})
    return result


def generate_image_frames(video_path: str, output_folder="../.cache"):
    frames = extract_frames(video_path, output_folder)
    return {"video": os.path.basename(video_path), "frames": frames}


def multi_process_videos(video_folder: str):
    files = list(glob.iglob(f"{video_folder}/*.mp4"))
    pool = Pool(6)

    # batch
    batches, batch = [], []
    for file in files:
        batch.append(file)
        if len(batch) >= 12:
            batches.append(batch)
            batch = []
    if len(batch):
        batches.append(batch)
    
    for batch in tqdm(batches):
        with open("../.cache/framefiles.jsonl", "a+", encoding="utf-8") as f:
            for video_frames in pool.map(generate_image_frames, batch):
                print(json.dumps(video_frames), file=f)


def extract_frames(video_path, output_folder="../.cache", interval=1):
    title = os.path.basename(video_path).replace(".mp4", "")
    frame_paths = []
    # Create the output directory if it doesn't exist
    if not os.path.exists(os.path.join(output_folder, title)):
        os.makedirs(os.path.join(output_folder, title))

    # Capture the video
    cap = cv2.VideoCapture(video_path)

    # Get the frame rate of the video
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * interval)  # Frame interval for 1-second intervals

    frame_count = 0
    success, frame = cap.read()

    while success:
        # Check if this frame is at the desired interval
        if frame_count % frame_interval == 0:
            # Save the frame as an image
            frame_filename = os.path.join(output_folder, title, f"frame_{frame_count // frame_interval}.jpg")
            cv2.imencode('.jpg', frame)[1].tofile(frame_filename)
            frame_paths.append(frame_filename)

        # Read the next frame
        success, frame = cap.read()
        frame_count += 1

    cap.release()
    return frame_paths


if __name__ == '__main__':
    # multi_process_videos("D:/tools/BBDown/崩坏3剧情_崩坏三剧情CG＋对话整理")

    run_ocr_for_video()