import re
from typing import List
from uttut.elements import Datum, Intent, Entity


SUB_PROG = re.compile(r'<.*?>')
FINDALL_PROG = re.compile(r'<(.*?)>(.*?)</')


def remove_annotation(annotated_sentence: str):
    return SUB_PROG.sub('', annotated_sentence)


def transform_annotated_sentence_to_entity_object(
        annotated_sentence: str,
        clean_sentence: str = None,
        entity2replacements: dict = None,
    ) -> List[Entity]:
    if entity2replacements is None:
        entity2replacements = {}
    if clean_sentence is None:
        clean_sentence = remove_annotation(annotated_sentence)

    entity_word_pair = FINDALL_PROG.findall(annotated_sentence)
    entities = []
    begin_index = 0
    for entity, word in entity_word_pair:
        start_idx = clean_sentence.find(word, begin_index)
        if start_idx == -1:
            raise ValueError(
                'Word {} can not be found in {}'.format(word, clean_sentence),
            )
        begin_index = start_idx + len(word)
        if entity not in entity2replacements:
            replacements = None
        else:
            replacements = entity2replacements[entity]
        entities.append(
            Entity(
                name=entity,
                start=start_idx,
                end=begin_index,
                value=word,
                replacements=replacements,
            ),
        )
    return entities


def transform_annotated_sentence_to_datum(
        annotated_sentence: str,
        intents: List[str] = None,
        entity2replacements: dict = None,
    ) -> Datum:
    clean_sentence = remove_annotation(annotated_sentence)
    if intents is None:
        list_of_intents = None
    else:
        list_of_intents = [Intent(intent) for intent in intents]
    return Datum(
        utterance=clean_sentence,
        intents=list_of_intents,
        entities=transform_annotated_sentence_to_entity_object(
            annotated_sentence=annotated_sentence,
            clean_sentence=clean_sentence,
            entity2replacements=entity2replacements,
        ),
    )


def transform_annotated_sentences_to_data(
        annotated_sentences: List[str],
        intents: List[List[str]] = None,
        entity2replacements: dict = None,
    ):
    if entity2replacements is None:
        entity2replacements = {}

    if intents is not None:
        if len(intents) != len(annotated_sentences):
            raise ValueError(
                'num of intents is not equal to num of annotated sentences',
            )
        data = []
        for annotated_sentence, intents_for_datum in zip(annotated_sentences, intents):
            datum = transform_annotated_sentence_to_datum(
                annotated_sentence=annotated_sentence,
                intents=intents_for_datum,
                entity2replacements=entity2replacements,
            )
            data.append(datum)
    else:
        data = []
        for annotated_sentence in annotated_sentences:
            datum = transform_annotated_sentence_to_datum(
                annotated_sentence=annotated_sentence,
                intents=intents,
                entity2replacements=entity2replacements,
            )
            data.append(datum)
    return data
