from typing import Sequence, NamedTuple
import re
import string
from collections import Counter

class Mention(NamedTuple):
    entity_type: str
    start: int
    end: int # exclusive

BEGIN = "B"
INSIDE = "I"
OUTSIDE = "O"
DELIM = "-"

def decode_mentions(annotated_text: str, clean_text: list[str]) -> list[Mention]:
    pattern = re.compile(r'\[([A-Z]+)\](.*?)\[/\1\]')
    result = []
    for match in pattern.finditer(annotated_text):
        entity_type = match.group(1)
        entity_text = match.group(2)
        word_list = split_text(entity_text)
        start = clean_text.index(word_list[0])
        end = clean_text.index(word_list[-1]) + 1
        result.append(Mention(entity_type, start, end))
    return result


def encode_bio(tokens: Sequence[str], mentions: Sequence[Mention]) -> list[str]:
    target = [OUTSIDE] * len(tokens)
    for item in mentions:
        b_name = BEGIN + DELIM + item.entity_type
        i_name = INSIDE + DELIM + item.entity_type
        target[item.start] = b_name
        if item.start + 1 != item.end:
            for i in range(item.start + 1, item.end):
                target[i] = i_name
    return target

def split_text(text: str) -> list[str]:
    # john 's two - handed
    return re.findall(r"\w+(?=-)|-|\w+(?=')|'\w+|\w+|\.{3}|[^\w\s]", text)
    # seperate john 's two -handed
    #return re.findall(r"\w+(?=-)|-\w+|\w+(?=')|'\w+|\w+|\.{3}|[^\w\s]", text)
    # keep john's
    #return re.findall(r"\w+(?:'\w+)*|-\w+|\w+|\.{3}|[^\w\s]", text)

def decode_bio(labels: list[str]) -> list[Mention]:
    processing = {"entity": None, "start": None, "end": None}
    result = []
    for i, item in enumerate(labels):
        if item == OUTSIDE:
            if processing["end"] is not None:
                processing["end"] = i
                result.append(Mention(processing["entity"], processing["start"], processing["end"]))
                processing = {"entity": None, "start": None, "end": None}
        else:
            if item[0] == BEGIN:
                if processing["end"] is not None:
                    processing["end"] = i
                    result.append(Mention(processing["entity"], processing["start"], processing["end"]))
                    processing = {"entity": None, "start": None, "end": None}
                processing["entity"] = item[2:]
                processing["start"] = i
                processing["end"] = i
            if item[0] == INSIDE:
                if processing["end"] is None:
                    processing["entity"] = item[2:]
                    processing["start"] = i
                    processing["end"] = i
                else:
                    tag = item[2:]
                    if tag == processing["entity"]:
                        processing["end"] = i
                    else:
                        processing["end"] += 1
                        result.append(Mention(processing["entity"], processing["start"], processing["end"]))
                        processing["entity"] = tag
                        processing["start"] = i
                        processing["end"] = i
    if processing["end"] is not None:
        processing["end"] += 1
        result.append(Mention(processing["entity"], processing["start"], processing["end"]))
    return result

'''
def compare_mentions(mentions_list):
    all_mentions = [mention for sublist in mentions_list for mention in sublist]
    mention_counter = Counter(all_mentions)
    result = []
    for mention, count in mention_counter.items():
        if count >= 3:
            result.append(mention)
    return result
'''

'''
# functional test
text = "A single-edged sword seldom seen in Hyrule. This weapon is passed down through the Sheikah tribe and has an astonishingly shape edge ideal for slicing."
clean_text = split_text(text)
print(clean_text)
annotated_text = "A single-edged sword seldom seen in [LOCA]Hyrule[/LOCA]. This weapon is passed down through the [CREA]Sheikah tribe[/CREA] and has an astonishingly shape edge ideal for slicing."

mentions = decode_mentions(annotated_text, clean_text)
print(mentions)
tagged_text = encode_bio(clean_text, mentions)
print(tagged_text)
decoded_mentions = decode_bio(tagged_text)
print(decoded_mentions)
'''