from google import genai
from google.genai import types
from google.genai import errors
import time
import os

import json
import tqdm

from description_prompt import SYSTEM_PROMPT
from mention import Mention, decode_mentions, encode_bio, decode_bio, split_text


os.environ['GEMINI_API_KEY'] = ''
client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

# Gemini API
def call_gemini(prompt, model='gemini-2.5-pro-preview-03-25', temperature=0.5, top_k=30, candidate_count=5,
        max_tokens=2560):

    try:
        ans = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=max_tokens,
                top_k=top_k,
                temperature=temperature,
                candidate_count=candidate_count
            ),
        )
        return ans.candidates
    except errors.APIError as e:
        time.sleep(1)
    raise RuntimeError('Failed to call GEMINI API')


INPUT_PATH = 'dataset/train.jsonl'
OUTPUT_PATH = 'dataset/train_annotation.jsonl'
instances = list(map(json.loads, open(INPUT_PATH)))

with open(OUTPUT_PATH, "w") as f:
    for item in tqdm.tqdm(instances):
        text = item["text"]
        response = call_gemini(
            text,
            model='gemini-2.5-pro-preview-03-25',
            temperature=0,
            top_k=1,
            candidate_count=1,
            max_tokens=2560
        )

        output = {
            "text": text,
            "candidates": [canidate.content.parts[0].text for canidate in response],
            "original_label": item["label"],
        }
        f.write(json.dumps(output, ensure_ascii=False) + '\n')
        f.flush()
        