# cython: profile=True
# cython: linetrace=False
from typing import List, Tuple

from uttut.elements import Datum, Entity
from uttut import ENTITY_LABEL


def _gen_partitioned_utterance_n_entities(
        datum: Datum,
        not_entity: str = ENTITY_LABEL['NOT_ENTITY'],
    ):

    start = 0
    utterance = datum.utterance
    partitioned_utterance = []
    partitioned_entities = []

    if datum.has_entities():
        for entity in datum.entities:
            if start != entity.start:
                partitioned_utterance += [
                    utterance[start: entity.start]]
                partitioned_entities.append(not_entity)
            partitioned_utterance += [
                utterance[entity.start: entity.end]]
            partitioned_entities.append(entity.name)
            start = entity.end

        if datum.entities[-1].end != len(utterance):
            partitioned_utterance += [utterance[start:]]
            partitioned_entities.append(not_entity)
    else:
        partitioned_utterance = [utterance]
        partitioned_entities = [not_entity]

    if len(partitioned_utterance) != len(partitioned_entities):
        raise KeyError(
            'Number of segments of utterance and entities is not equal',
            'partitioned_utterance = {}, \n partitioned_entities = {}'.format(
                partitioned_utterance, partitioned_entities,
            ),
        )

    return partitioned_utterance, partitioned_entities


cpdef normalize_datum(
        datum: Datum,
        text_normalizer=None,
        not_entity=ENTITY_LABEL['NOT_ENTITY'],
    ):
    cdef int idx
    cdef int n_parts
    cdef int begin_ind
    cdef int start
    cdef list entities
    cdef str normalized_segment
    cdef int entities_ind
    cdef str normalized_utterance

    if text_normalizer is None:
        return datum, None

    normalized_utterance, meta = text_normalizer.normalize(
        sentence=datum.utterance,
    )
    if not datum.has_entities():
        return Datum(
            utterance=normalized_utterance,
            intents=datum.intents,
        ), meta
    else:
        partitioned_utterance, partitioned_entities = \
            _gen_partitioned_utterance_n_entities(
                datum=datum,
                not_entity=not_entity,
            )
        begin_ind = 0
        entities = []
        entities_ind = 0
        n_parts = len(partitioned_utterance)
        for idx in range(n_parts):
        # for segment, entity in zip(partitioned_utterance, partitioned_entities):
            segment = partitioned_utterance[idx]
            entity = partitioned_entities[idx]
            normalized_segment, _ = text_normalizer.normalize(
                sentence=segment,
            )
            start = normalized_utterance.find(
                normalized_segment,
                begin_ind,
            )
            if start == -1:
                raise KeyError(
                    'String match fails when normalizing datum, '
                    'original utterance = {},\n normalized_utterance = {},\n'.format(
                        datum.utterance,
                        normalized_utterance,
                    ),
                    'utterance split by entity = {},\n entities = {}.\n'.format(
                        partitioned_utterance,
                        partitioned_entities,
                    ),
                )
            begin_ind = start + len(normalized_segment)
            if entity != not_entity:
                entities.append(
                    Entity(
                        name=entity,
                        value=normalized_segment,
                        start=start,
                        end=begin_ind,
                        replacements=datum.entities[entities_ind].replacements,
                    ),
                )
                entities_ind += 1

    return Datum(
        utterance=normalized_utterance,
        intents=datum.intents,
        entities=entities,
    ), meta


def denormalize_datum(
        datum: Datum,
        meta: List[dict],
        text_normalizer: object = None,
        not_entity=ENTITY_LABEL['NOT_ENTITY'],
    ) -> Datum:

    if text_normalizer is None:
        return datum

    denormalized_utterance = text_normalizer.denormalize(
        sentence=datum.utterance,
        meta=meta,
    )
    if not datum.entities:
        return Datum(
            utterance=denormalized_utterance,
            intents=datum.intents,
        )
    else:
        partitioned_utterance, partitioned_entities = \
            _gen_partitioned_utterance_n_entities(
                datum=datum,
                not_entity=not_entity,
            )

        utterance_with_wall = '|IamtheWALL|'.join(partitioned_utterance)
        denormalized_utterance_with_wall = text_normalizer.denormalize(
            sentence=utterance_with_wall,
            meta=meta,
        )
        partitioned_denormalized_utterance = \
            denormalized_utterance_with_wall.split('|IamtheWALL|')

        if len(partitioned_utterance) != len(partitioned_denormalized_utterance):
            raise KeyError(
                'Something wrong during denormalize',
                'partitioned_utterance is {}'.format(partitioned_utterance),
                'after denormalize = {}'.format(
                    partitioned_denormalized_utterance),
            )

        begin_ind = 0
        entities_ind = 0
        entities = []
        for denormalized_segment, entity in zip(
            partitioned_denormalized_utterance,
            partitioned_entities,
        ):
            start = denormalized_utterance.find(
                denormalized_segment,
                begin_ind,
            )
            if start == -1:
                raise KeyError(
                    'String match fails, str = {}, substr = {}'.format(
                        denormalized_utterance,
                        denormalized_segment,
                    ),
                )

            begin_ind = start + len(denormalized_segment)

            if entity != not_entity:
                entities.append(
                    Entity(
                        name=entity,
                        value=denormalized_segment,
                        start=start,
                        end=begin_ind,
                        replacements=datum.entities[entities_ind].replacements,
                    ),
                )
                entities_ind += 1

    return Datum(
        utterance=denormalized_utterance,
        intents=datum.intents,
        entities=entities,
    )
