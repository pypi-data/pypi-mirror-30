# cython: profile=True
# cython: linetrace=False
import random
from typing import List, Tuple
import numpy as np
from .elements import (
    Datum,
    Entity,
)


__all__ = [
    'expand_by_entities',
]


cdef int greatest_common_divisor(int x, int y) nogil:
    """This function implements the Euclidian algorithm
    to find G.C.D. of two numbers"""
    while y:
        x, y = y, x % y
    return x


cdef int least_common_multiple(int x, int y) nogil:
    """This function takes two
    integers and returns the L.C.M."""

    cdef int lcm = (x * y) // greatest_common_divisor(x, y)
    return lcm


cdef int least_common_multiple_for_list_of_number(list list_of_number):
    cdef int lcm
    cdef int number
    cdef int idx
    cdef int len_list_of_number = len(list_of_number)
    for idx in range(len_list_of_number):
        number = list_of_number[idx]
        if idx == 0:
            lcm = number
        else:
            lcm = least_common_multiple(lcm, number)
    return lcm


def augment_single_partition_utterances(
        partitioned_utterance,
        sorted_entities,  # List[Entity]
        random_shuffle=False,
        random_seed=2018,
    ):
    cdef list n_replacements = [entity.n_replacements() for entity in sorted_entities]
    cdef int lcm = least_common_multiple_for_list_of_number(n_replacements)

    complete_set_size = max(n_replacements)

    if complete_set_size > 1:
        sorted_entities = sorted(
            sorted_entities,
            key=lambda x: x.n_replacements(),
        )

        #### TODO: NEED BETTER THRESHOLD
        if lcm > 5000:
            data_size = int(5000 + np.sqrt(lcm - 5000))
            if data_size < complete_set_size:
                data_size = complete_set_size
        else:
            data_size = lcm

        output = _augment_partition_utterance_number_less_than_lcm(
            partitioned_utterance=partitioned_utterance,
            sorted_entities=sorted_entities,
            data_size=data_size,
            random_shuffle=random_shuffle,
            random_seed=random_seed,
        )
    else:
        output = [partitioned_utterance]
    return output


def augment_single_partition_utterances_with_upper_bound(
        partitioned_utterance,
        sorted_entities,  # List[Entity]
        upper_bound,
        random_shuffle=False,
        random_seed=2018,
    ):
    cdef list n_replacements = [entity.n_replacements() for entity in sorted_entities]
    cdef lcm = least_common_multiple_for_list_of_number(n_replacements)

    if lcm > upper_bound:
        data_size = upper_bound
    else:
        data_size = lcm
    complete_set_size = max(n_replacements)

    output = _augment_partition_utterance_number_less_than_lcm(
        partitioned_utterance=partitioned_utterance,
        sorted_entities=sorted_entities,
        data_size=data_size,
        random_shuffle=random_shuffle,
        random_seed=random_seed,
    )
    return output


cdef list _augment_partition_utterance_number_less_than_lcm(
        list partitioned_utterance,  # List[str]
        list sorted_entities,  # List[Entity]
        int data_size,
        bint random_shuffle=False,
        int random_seed=2018,
    ):
    cdef list init_indices = []
    cdef list output = []

    random.seed(random_seed)
    if random_shuffle:
        init_indices = [random.randrange(entity.n_replacements()) for entity in sorted_entities]
    else:
        init_indices = [0 for _ in range(len(sorted_entities))]

    for idx in range(data_size):
        partitioned_utterance_copy = partitioned_utterance[:]
        for entity, init_index in zip(sorted_entities, init_indices):
            if entity.no_replacements():
                continue
            r_idx = (idx + init_index) % entity.n_replacements()
            if r_idx != 0:
                partitioned_utterance_copy[entity.index] = \
                    list(entity.replacements)[r_idx - 1]
        output += [partitioned_utterance_copy]
    return output


def gen_partitioned_utterance(
        utterance: str,
        sorted_entities: list,  # List[Entity]
    ) -> Tuple[List, List]:

    start = 0
    partitioned_utterance = []

    for num, entity in enumerate(sorted_entities):
        if start != entity.start:
            partitioned_utterance += [utterance[start: entity.start]]
        partitioned_utterance += [utterance[entity.start: entity.end]]
        sorted_entities[num].index = len(partitioned_utterance) - 1
        start = entity.end

    if sorted_entities[-1].end != len(utterance):
        partitioned_utterance += [utterance[start:]]

    return sorted_entities, partitioned_utterance


def partition_by_entities(datum: Datum) -> Tuple[List[dict], List[dict]]:
    # entities = [entity.to_dict() for entity in datum.entities]
    new_entities, parts = gen_partitioned_utterance(
        sorted_entities=datum.entities,
        utterance=datum.utterance,
    )
    return new_entities, parts


cdef _include_orig_value(
        entities_with_index: List[Entity],
        parts: List[str],
    ):
    new_entities = entities_with_index.copy()
    for entity in new_entities:
        target_idx = entity['index']
        replacements = entity.get('replacements', [])
        replacements.append(parts[target_idx])
        entity['replacements'] = replacements
    return new_entities


cdef _aggregate_entities(
        list parts,
        list entities_with_index,
        bint include_replacements,
    ):

    cdef list entities = []
    cdef int pointer = 0
    cdef int idx
    cdef int n_parts = len(parts)
    cdef int n_entities = len(entities_with_index)
    cdef int len_part
    cdef set replacements
    cdef str part
    cdef dict index2entity = {}

    for idx in range(n_entities):
        obj = entities_with_index[idx]
        index2entity[obj.index] = obj

    for idx in range(n_parts):
        part = parts[idx]
        len_part = len(part)
        if idx in index2entity:
            entity = index2entity[idx]
            if include_replacements:
                replacements = entity.replacements_with_self - set([part])
                entities.append(Entity(
                    name=entity.name,
                    value=part,
                    start=pointer,
                    end=pointer + len_part,
                    replacements=list(replacements),
                ))
            else:
                entities.append(Entity(
                    name=entity.name,
                    value=part,
                    start=pointer,
                    end=pointer + len_part,
                ))
        pointer += len_part
    return entities


cpdef expand_by_entities(
        datum,
        augment_method,
        dict augment_params=None,
        bint include_replacements=False,
    ):
    if augment_params is None:
        augment_params = {}

    if not datum.has_entities():
        return [datum]
    entities_with_index, parts = partition_by_entities(datum)

    augmented_parts = augment_method(
        partitioned_utterance=parts,
        sorted_entities=entities_with_index,
        **augment_params,
    )

    # included_entities_with_index = _include_orig_value(entities_with_index, parts)

    result = []
    for parts in augmented_parts:
        utterance = ''.join(parts)
        entities = _aggregate_entities(parts, entities_with_index, include_replacements)
        new_datum = Datum(
            utterance=utterance,
            intents=datum.copy_intents(),
            entities=entities,
        )
        result.append(new_datum)
    return result
