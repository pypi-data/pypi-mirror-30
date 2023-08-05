from typing import List
from collections import Counter

from uttut.elements import Datum
from nlu.tokenizers import CustomJiebaTokenizer

TOKENIZER = CustomJiebaTokenizer()


def longest_common_substring(s1: str, s2: str):
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]


def collect_tokens_for_tokenizer(data: List[Datum])-> List[str]: # noqa
    tokens = []
    for datum in data:
        if datum.entities is not None:
            for entity in datum.entities:
                tokens.append([entity.value])
                tokens.append(list(entity.replacements))
    unique_tokens = set(sum(tokens, []))

    raw_minimal_tokens = TOKENIZER.lcut(' '.join(unique_tokens))

    tokens2frequency = Counter(raw_minimal_tokens).most_common()

    if tokens2frequency[0][0] == ' ':
        tokens2frequency = tokens2frequency[1:]

    output = {}
    for i, (token, freq) in enumerate(tokens2frequency):
        if i == 0:
            output[token] = freq
        else:
            min_overlapped = 9999
            for output_token, _ in output.items():
                overlapped_diff = len(token) - len(
                    longest_common_substring(
                        s1=token,
                        s2=output_token,
                    ),
                )
                if overlapped_diff < min_overlapped:
                    min_overlapped = overlapped_diff

            if min_overlapped > 1:
                output[token] = freq

    if ' ' in output:
        del output[' ']

    return sorted(output.items(), key=lambda x: x[1], reverse=True)


def get_tokens_from_replacements(data: List[Datum]) -> List[str]:
    unique_entities = []
    tokens = []
    for datum in data:
        if datum.has_entities():
            for entity in datum.entities:
                if entity.name not in unique_entities:
                    tokens.append(list(entity.replacements))
                    unique_entities.append(entity.name)
    return set(sum(tokens, []))
