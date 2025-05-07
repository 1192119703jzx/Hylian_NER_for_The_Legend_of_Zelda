from mention import Mention, decode_mentions, encode_bio, decode_bio, split_text

import json

DATA_PATH = 'dataset/dev_annotation.jsonl'
OUTPUT_PATH = 'dataset/dev_BIO.jsonl'

with open(DATA_PATH, "r", encoding='utf-8') as f:
    instances = list(map(json.loads, f))

with open(OUTPUT_PATH, "w") as f:
    for item in instances:
        try:
            text = item["text"]
            annotated_text = item["candidates"][0]
            clean_text = split_text(text)
            #print(clean_text)

            # Decode the mentions from the annotated text
            mentions = decode_mentions(annotated_text, clean_text)
            # Encode the mentions into BIO format
            BIO_labels = encode_bio(clean_text, mentions)
            result = {'text': clean_text, 'label': BIO_labels}
            
            f.write(json.dumps(result, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Error processing item: {item}")
            print(f"Exception: {e}")

