from typing import List

from uttut.elements import Datum
from uttut import ENTITY_LABEL


def get_unique_entities(
        data: List[Datum],
        need_start_end: str = False,
    )-> List:
    unique_entities = []
    for datum in data:
        if datum.entities is not None:
            for entity in datum.entities:
                unique_entities.append(entity.name)
    unique_entities = list(set(unique_entities))

    start_end_list = []
    if need_start_end is True:
        for entity in unique_entities:
            start_end_list.append(entity + ENTITY_LABEL['SUFFIX_START'])
            start_end_list.append(entity + ENTITY_LABEL['SUFFIX_END'])
        unique_entities += start_end_list

    return unique_entities
