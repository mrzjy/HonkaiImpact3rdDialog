import json
import re
from collections import Counter

from nltk import edit_distance
from tqdm import tqdm

map_video_to_frames = {}


def parse_vlm(string):
    try:
        result = json.loads(string.split("```json")[-1].split("```")[0])
        if result["type"] is None or result.get("content") is None:
            return None
        if result["type"] not in {"dialogue", "narration"}:
            return None
        if not isinstance(result["content"], str):
            return None
        if re.match("^[<>a-zA-Z ]+$", result["content"]):
            return None
        if result["type"] == "dialogue":
            if not result["role"]:
                result = {"type": "dialogue", "role": "<unknown>", "content": result["content"]}
            else:
                if "<" in result["role"]:
                    result["role"] = "<unknown>"
                elif re.match("^[?？ ]+$", result["role"]):
                    result["role"] = "？？？"
        else:
            result["role"] = "narration"
        if not re.search("[a-zA-Z]", result["content"]):
            result["content"] = result["content"].replace(" ", "")
            result["content"] = result["content"].replace(",\s*", "，")
            result["content"] = result["content"].replace("...", "…")
            result["content"] = result["content"].replace("【", "「")
            result["content"] = result["content"].replace("】", "」")
            result["content"] = result["content"].replace("『", "「")
            result["content"] = result["content"].replace("』", "」")
            result["content"] = re.sub("…[·\.]+", "……", result["content"])
            result["content"] = re.sub("·{1,}", "……", result["content"])

        result = {k: result[k] for k in ["type", "role", "content"]}

        if "state" in result:
            del result["state"]
        return result
    except:
        return None


def is_subset_of(a, b):
    longer_one = a if len(a) > len(b) else b
    if a == b:
        return True, longer_one
    if (a[:-1] in b[:len(a)] and len(a) > 5) or a[:12] in b:
        return True, longer_one
    ed = edit_distance(a, b)
    if ed < len(longer_one)//3:
        print(ed, a, b)
        return True, longer_one
    return False, longer_one


with open("../.cache/vlm_output.jsonl", "r", encoding="utf-8") as f:
    for l in tqdm(f):
        vlm = json.loads(l)
        if vlm["video"] not in map_video_to_frames:
            map_video_to_frames[vlm["video"]] = []

        vlm_output = parse_vlm(vlm["vlm"])
        if vlm_output is None:
            continue

        if map_video_to_frames[vlm["video"]]:
            is_subset, longer_one = is_subset_of(
                map_video_to_frames[vlm["video"]][-1]["content"],
                vlm_output["content"],
            )
            if is_subset:
                vlm_output["content"] = longer_one
                map_video_to_frames[vlm["video"]][-1] = vlm_output
                continue

        map_video_to_frames[vlm["video"]].append(vlm_output)


count = 0
counter = Counter()
with open("../data/honkai_impact_3rd_chinese_corpus.jsonl", "w", encoding="utf-8") as f:
    for i, (key, values) in enumerate(map_video_to_frames.items()):
        key = key.split(".mp4")[0]
        key = re.sub("\[[^\[\]]+]", "", key)

        for j, v in enumerate(values):
            sample = {"chapter": key, "chapter_id": i, "utter_id": f"{i}-{j}"}
            for k, vv in v.items():
                if vv:
                    sample[k] = vv
                else:
                    sample[k] = ""
                    print(k)
            counter.update([v["type"]])
            print(json.dumps(sample, ensure_ascii=False), file=f)

print(count)
print(counter)