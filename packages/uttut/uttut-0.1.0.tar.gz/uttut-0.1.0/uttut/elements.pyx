from typing import List, Iterable
cimport cython

from .exceptions import (
    EntityOverlapping,
    EntityPositionError,
)
from .utils import (
    entity_position_correct,
    overlap,
    msg_entity_wrong_position,
    msg_entity_overlapping,
)



cdef class Entity:

    cdef public str name
    cdef public str value
    cdef public int start
    cdef public int end
    cdef public set replacements
    cdef public set replacements_with_self
    cdef public int index

    def __init__(
            self,
            str name,
            str value,
            int start,
            int end,
            replacements: Iterable[str] = None,
        ) -> None:
        self.index = -1

        self.name = name
        self.value = value
        self.start = start
        self.end = end
        cdef list _replacements = [] if replacements is None else list(replacements)
        self.replacements = set(_replacements)
        _replacements.append(self.value)
        self.replacements_with_self = set(_replacements)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('can only compare entity to entity')
        cdef bint same_name = self.name == other.name
        cdef bint same_value = self.value == other.value
        cdef bint same_position = (self.start == other.start) and (self.end == other.end)
        cdef bint same_replacements = self.replacements == other.replacements
        if same_name and same_value and same_position and same_replacements:
            return True
        return False

    def __repr__(self):
        return "<Entity {}: {} at {} - {}, with replacements: {}>".format(
            self.name,
            self.value,
            self.start,
            self.end,
            ', '.join(list(self.replacements)),
        )

    def no_replacements(self) -> bool:
        return len(self.replacements) == 0

    def n_replacements(self):
        return len(self.replacements) + 1

    def to_dict(self) -> dict:
        result = {
            'name': self.name,
            'start': self.start,
            'end': self.end - 1,
        }
        if not self.no_replacements():
            result['replacements'] = list(self.replacements)
        return result

    @classmethod
    def from_dict(cls, dict entity, str utterance):
        new_end = entity['end'] + 1
        entity_value = utterance[entity['start']: new_end]
        replacements = entity.get('replacements')
        return cls(
            name=entity['name'],
            value=entity_value,
            start=entity['start'],
            end=new_end,
            replacements=[] if replacements is None else replacements,
        )


cdef class Intent:

    cdef public str name

    def __init__(self, str name):
        self.name = name

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


class Datum:

    def __init__(
            self,
            str utterance,
            list intents = None,  # : List[Intent] = None,
            list entities = None,  # : List[Entity] = None,
        ):
        self.utterance = utterance
        self.intents = [] if intents is None else sorted(intents, key=lambda i: hash(i))
        self.entities = [] if entities is None else sorted(entities, key=lambda e: e.start)

        # check entity has correct value and position
        for entity in self.entities:
            if not entity_position_correct(self.utterance, entity):
                raise EntityPositionError(msg_entity_wrong_position(self.utterance, entity))

        # check overlapping entities
        for idx in range(len(self.entities) - 1):
            entity = self.entities[idx]
            next_entity = self.entities[idx + 1]
            if overlap(entity, next_entity):
                raise EntityOverlapping(msg_entity_overlapping(self.utterance, entity, next_entity))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('can only compare datum to datum')

        if not self.has_same_utterance_as(other):
            return False
        elif not self.has_same_intents_as(other):
            return False
        elif not self.has_same_entities_as(other):
            return False
        else:
            return True

    def __repr__(self):
        return "<Datum {} {} with entities: {}>".format(
            self.utterance,
            self.intents,
            self.entities,
        )

    def has_same_utterance_as(self, other):
        return self.utterance == other.utterance

    def has_same_intents_as(self, other):
        return set(self.intents) == set(other.intents)

    def has_same_entities_as(self, other):
        same_entities = False
        if len(self.entities) == len(other.entities):
            for self_entity, other_entity in zip(self.entities, other.entities):
                if self_entity != other_entity:
                    break
            else:
                same_entities = True
        return same_entities

    def has_entities(self):
        return len(self.entities) > 0

    def has_intents(self):
        return len(self.intents) > 0

    def copy_intents(self) -> List[Intent]:
        return [Intent(intent.name) for intent in self.intents]

    @classmethod
    def from_dict(cls, utterance_obj):
        utterance = utterance_obj['utterance']
        intents = []
        if isinstance(utterance_obj['intent'], str):
            intents.append(Intent(utterance_obj['intent']))
        elif isinstance(utterance_obj['intent'], dict):
            for intent in utterance_obj['intent']['names']:
                intents.append(Intent(intent))
        entities = None
        if utterance_obj.get('entities') is not None:
            entities = []
            for entity in utterance_obj['entities']:
                entities.append(Entity.from_dict(entity, utterance_obj['utterance']))
        return cls(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )

    def to_dict(self) -> dict:
        result = {
            'utterance': self.utterance,
            'intent': {'names': [intent.name for intent in self.intents]},
        }
        if len(self.entities) > 0:
            result['entities'] = [entity.to_dict() for entity in self.entities]
        return result
