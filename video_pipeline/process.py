import json
import os
import re
import shutil
from collections import Counter

from tqdm import tqdm


def is_subset_of(ocr_a: list, ocr_b: list, counter: Counter):
    a_string = " || ".join([o['text'] for o in ocr_a])
    b_string = " || ".join([o['text'] for o in ocr_b])

    if len(a_string) == len(b_string):
        return True

    for res_a, res_b in zip(ocr_a, ocr_b):
        regexp = res_a['text'].replace("?", "\?").replace(".", "\.").replace("*", "\*").replace(
            "[", "\[").replace("]", "\]").replace("+", "\+").replace("(", "\(").replace(")", "\)")
        # do not account for low scored ocr results
        if res_a["score"] < 0.95 or res_b["score"] < 0.95:
            continue

        if len(res_a["text"]) > 10:
            if res_a["text"] in b_string:
                return True

        try:
            if len(res_a["text"]) > 5 and counter[res_a["text"]] < 30 and re.search(f"^{regexp}", res_b["text"]):
                return True
        except:
            print(regexp)
    return False


def is_valid_frame(ocr: list):
    if not ocr:
        return False
    text = " ".join(o['text'] for o in ocr)
    if re.search("[M]i[Hh]o[Yy]o", text):
        return False
    if any("已完成" in o["text"] for o in ocr):
        return False
    return True


def is_valuable_ocr(ocr: dict):
    if not ocr:
        return False
    if ocr["score"] < 0.94:
        return False
    if re.search("[·○a-zA-Z0-9(<（/ ]*(历史|自动中|自动|跳过|移动指针|隐藏|显示|确定|返回|SOUND|ONLY|Enter|hits|INFO|SP|Splendid|Side Quest|Reward|Marvelous|Terrific|Great|Good|FPS|DOWN|UP|B|L)[·○）)/>a-zA-Z0-9 ]*", ocr["text"]):
        return False
    if re.match("^[a-zA-Z0-9]+[:/-][a-zA-Z0-9]+$", ocr["text"]):
        return False
    if re.match("^[0-9]+$", ocr["text"]):
        return False
    return True


def preprocess_frames(frames: list, counter: Counter):
    processed_frames = []
    for ocr in sorted(frames, key=lambda f: int(f["frame"].split("frame_")[-1].split(".jpg")[0])):
        """不客气，菲洛，我很擅长修理。对了，劳迪丝跑到哪里去了，怎么没有看到它"""
        if processed_frames and is_subset_of(processed_frames[-1]["ocr"], ocr["ocr"], counter):
            processed_frames[-1] = ocr
        else:
            processed_frames.append(ocr)
    return processed_frames


def copy_image(src_path, dest_path):
    try:
        # Check if the source file exists
        if not os.path.exists(src_path):
            print("Source file does not exist.")
            return

        # Copy the file
        shutil.copy2(src_path, dest_path)
        # print(f"Image successfully copied to {dest_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    map_video_to_frames = {}
    counter = Counter()
    samples = []

    with open("../.cache/ocr_results.jsonl", "r", encoding="utf-8") as f:
        for i, l in enumerate(tqdm(f, desc="loading data")):
            ocr = json.loads(l)
            if not is_valid_frame(ocr["ocr"]):
                continue
            ocr["ocr"] = [o for o in ocr["ocr"] if is_valuable_ocr(o)]
            for o in ocr["ocr"]:
                counter.update([o["text"]])

            samples.append(ocr)

        for ocr in samples:
            if ocr["video"] not in map_video_to_frames:
                map_video_to_frames[ocr["video"]] = []
            map_video_to_frames[ocr["video"]].append({"frame": ocr["frame"], "ocr": ocr["ocr"]})

    map_video_to_frames = {k: preprocess_frames(v, counter) for k, v in map_video_to_frames.items()}
    # for w, cnt in counter.most_common():
    #     if cnt > 50:
    #         print(w, cnt)

    os.makedirs("../tmp/img", exist_ok=True)
    cnt = 0
    with open("../tmp/ocr_input.jsonl", "w", encoding="utf-8") as f:
        for k, v in tqdm(map_video_to_frames.items()):
            video_name = os.path.basename(k)
            os.makedirs(os.path.join("../tmp/img", video_name), exist_ok=True)
            for j, frame in enumerate(v):
                img_name = os.path.basename(frame["frame"])
                dest_path = os.path.join("../tmp/img", video_name, img_name)
                copy_image(frame["frame"], dest_path)
                v[j]["frame"] = os.path.join("img", video_name, img_name)
                cnt += 1
            print(json.dumps({"video": k, "frames": [fr for fr in v if fr]}, ensure_ascii=False), file=f)
    print(cnt)
