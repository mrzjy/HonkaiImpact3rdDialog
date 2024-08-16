# HonkaiImpact3rdDialog
A project that collects Honkai Impact 3rd text corpus

本项目收集崩坏三游戏对话语料

- [x] Chinese Corpus
- [x] English Corpus

## Chinese Corpus

See [honkai_impact_3rd_chinese_dialogue_corpus](https://huggingface.co/datasets/mrzjy/honkai_impact_3rd_chinese_dialogue_corpus) for data download.

We apply "video-OCR -> VLM parsing" pipeline to get the corpus from [online videos](https://www.bilibili.com/video/BV12W411h76f).

### Video OCR

We apply solid OCR model to first recognize Chinese characters throughout video game playthrough.

- **Video download:** We apply [BBdown](https://github.com/nilaoda/BBDown) to download [Honkai Impact 3rd playthough videos](https://www.bilibili.com/video/BV12W411h76f).
- **Video to frames:** The videos are then split into image frames every 1 second.
- **OCR**: For each frame image, we apply [paddle-ocr](https://github.com/PaddlePaddle/PaddleOCR) for accurate OCR performance, resulting in texts & bounding boxes for each frame.

### VLM Parsing

We apply Multimodal LLM to perform finegrained image understanding:

- Given the images and corresponding OCR results, we prompt VLM to tell us whether there are narrations, or speaker & dialogue content, or irrelevant content.

Note:

- There are VLMs that can do OCR directly, we however add a OCR-step before applying VLMs, hoping to reduce VLM hallucinations.

## English Corpus

As for English corpus, this repo simply copies a fan-edit **English** game lore transcription google-doc that I encounter from [Reddit](https://www.reddit.com/r/houkai3rd/comments/152n9m7/is_there_anywhere_i_can_find_the_script_for/)

**All credits go to the authors!**

- Example snippet (Full content is in data folder)

```
...
Act 3 - Swept Away:
Gameplay 16-9 - Saving the Roost I:
Tesla: What the hell is going on?
Mei and Tesla were shocked by the scene they saw outside the Helios.
The sea that flooded the city was calm yesterday, but the water rose by more than 10 meters overnight.
Mei: This isn’t normal at all.
Mei: …The children might be in danger! We need to head to the Roost now!
Mei: No, Honkai beasts are gathering over there!
Sora: Hey! Mei!
Mei: Sora! I’m so glad you’re alright.
The children were busy moving the warehouse supplies. They were ill-prepared for the flood.
Tesla: All nearby Honkai beasts neutralised. Stay vigilant. We’ve gotta stay on guard.
Tesla: We must move the kids and supplies to higher ground. Tell them that I’m moving mechs into the shelters.
Sora: Oh… okay.


Gameplay 16-10 - Saving the Roost II:
Boom!
The residents vacated the lower levels of the Roost in less than 20 minutes.
Sora: Why did the flood waters rise? The city… has become very strange…
Mei: Dr. Tesla, I have a bad feeling about this.
Mei: The Honkai beasts are riled up, and they’re appearing in greater numbers, as if they’re… attracted to something.
Sora: Is it because of that… huge beast I saw yesterday?
Sora: I’ve never seen it before… it was like… the king of the monsters…
Mei: Where did you see it?
Sora: Near the Nagazora Wall. I can take you there.
Mei: This is urgent. We must investigate immediately.
...
```

## FAQs

1. Interested in some game corpus?

- [GenshinDialog](https://github.com/mrzjy/GenshinDialog)
- [StarrailDialog](https://github.com/mrzjy/StarrailDialogue)
- [ZZZDialog](https://github.com/mrzjy/ZZZDialog)
- [HonkaiImpact3rdDialog](https://github.com/mrzjy/HonkaiImpact3rdDialog)
- [ArknightsDialog](https://github.com/mrzjy/ArknightsDialog)
- [WutheringDialog](https://github.com/mrzjy/WutheringDialog)
- [hoyo_public_wiki_parser](https://github.com/mrzjy/hoyo_public_wiki_parser): Parse Hoyoverse public wiki data
