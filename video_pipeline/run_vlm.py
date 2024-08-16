import argparse
import traceback

from PIL import Image
import json
import os
import torch
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModel


def load_model(args):
    model = AutoModel.from_pretrained(args.model_dir, trust_remote_code=True,
                                      attn_implementation='sdpa',
                                      torch_dtype=torch.bfloat16)  # sdpa or flash_attention_2, no eager
    model = model.eval().cuda()
    tokenizer = AutoTokenizer.from_pretrained(args.model_dir, trust_remote_code=True)

    return model, tokenizer


def load_data_batch(data_path, batch_size):
    print("load", data_path)
    print("batch_size", batch_size)
    with open(data_path, "r", encoding="utf-8") as f:
        if data_path.endswith(".json"):
            samples = json.load(data_path)
        elif data_path.endswith(".jsonl"):
            samples = [json.loads(s) for s in f]
        else:
            raise NotImplementedError

    batch, batches = [], []
    for sample in samples:
        for f in sample["frames"]:
            f["video"] = sample["video"]
            if len(batch) == batch_size:
                batches.append(batch)
                batch = []
            batch.append(f)

    # last batch
    if len(batch):
        batches.append(batch)
    print("n batch:", len(batches))
    return batches


PROMPT = """This is an image of RPG game. Given associated OCR result, please help us identify the existence of story narrations and dialogues and extract them in structured format.
This is the associated OCR results:
```ocr
{ocr}
```

There are two types of story content you should extract:

- Narration: single line or paragraph of narration, telling the story background and plots
- Dialogue: dialogue contents spoken by a character. The speaker character name and spoken content must co-appear in the image.

Note:

- Be strict with OCR texts, you are NOT allowed to fabricate contents that are not captured by OCR results.
- The OCR often separate multiline texts, and it's your task to concatenate consecutive lines if necessary.
- There might be noisy textual contents (e.g., advertisement, UI elements, combos, etc.), which are not our interest.
- There might be texts indicating state/environment information (e.g., location, time, source, state, etc), you can extract them as well in environment field.

Please output your response in JSON structure in one of the 3 following ways:

1. In case of no desired content (neither dialogue nor narration), output a JSON dict whose type is null.

```json
{{"type": null}}
```

2. In case of dialogue

```json
{{
    "type": "dialogue",
    "role": "<speaker name>",
    "content": "<spoken content>",
    "state": "<state/environment info, null if there isn't any>"
}}
```

3. In case of narration

```json
{{
    "type": "narration",
    "content": "<narrative content>"
}}
```"""


def format_template(ocr):
    ocr_texts = []
    for o in ocr:
        ocr_texts.append(o["text"])
    prompt = PROMPT.format(ocr=str(ocr_texts))
    return prompt


def run(args):
    # load data
    batches = load_data_batch(args.data, args.batch_size)

    # load model
    model, tokenizer = load_model(args)

    # generate
    for batch in tqdm(batches):
        msgs = [
            [{"role": "user", "content": [Image.open("../tmp/" + b["frame"]), format_template(b["ocr"])]}]
            for b in batch
        ]
        outputs = model.chat(
            image=None,
            msgs=msgs,
            tokenizer=tokenizer
        )
        with open(args.output, "a+") as f:
            for s, o in zip(batch, outputs):
                s["vlm"] = o
                print(json.dumps(s, ensure_ascii=False), file=f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='../tmp/ocr_input.jsonl')
    parser.add_argument('--model_dir', default='path/to/model')
    parser.add_argument('--output', default='vlm_output.jsonl')
    parser.add_argument('--batch_size', default=20, type=int)
    args = parser.parse_args()

    run(args)
