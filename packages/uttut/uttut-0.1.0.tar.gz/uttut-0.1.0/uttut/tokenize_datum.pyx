# cython: profile=True
# cython: linetrace=False
from typing import List

from uttut.elements import Datum
from uttut import ENTITY_LABEL

from collections import Counter


def _get_entity_array(
        datum: Datum,
        not_entity: str = ENTITY_LABEL['NOT_ENTITY'],
    ):
    result = [not_entity] * len(datum.utterance)
    for entity in datum.entities:
        for ind in range(entity.start, entity.end):
            result[ind] = entity.name
    return result


def tokenize_datum(
        datum: Datum,
        tokenizer: object,
        lcut_params: dict = None,
        not_entity: str = ENTITY_LABEL['NOT_ENTITY'],
    ):

    if lcut_params is None:
        lcut_params = {'sentence': datum.utterance}
    else:
        lcut_params['sentence'] = datum.utterance

    tokenized_utterance = tokenizer.lcut(**lcut_params)
    entity_array = _get_entity_array(
        datum=datum,
        not_entity=not_entity,
    )
    utterance = datum.utterance
    entities = []
    begin_ind = 0
    for token in tokenized_utterance:
        start = utterance.find(token, begin_ind)
        if start != -1:
            entity_stat = Counter(
                entity_array[start: start + len(token)],
            )
            entity_stat = sorted(entity_stat.items(), key=lambda x: (-x[1], x[0]))
            if (entity_stat[0][0] == not_entity) and (len(entity_stat) > 1):
                entities.append(entity_stat[1][0])
            else:
                entities.append(entity_stat[0][0])
            begin_ind = start + len(token)
        else:
            raise ValueError(
                'Substring <{}> can not be found in string <{}>.'.format(
                    token,
                    utterance,
                ),
            )
    return tokenized_utterance, entities
