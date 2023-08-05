# -*- coding: utf-8 -*-
from unittest import TestCase
from uttut.elements import (
    Datum,
    Intent,
    Entity,
)
from .. annotated_sentence_transformer import (
    remove_annotation,
    transform_annotated_sentence_to_entity_object,
    transform_annotated_sentence_to_datum,
    transform_annotated_sentences_to_data,
)


class TransformAnnotatedSentenceTestCase(TestCase):

    def setUp(self):
        self.example_annotated_sentence = \
            '<人名>Kelly</人名>喜歡<人名>小白</人名>魔性的笑聲和吃<人名>豪大</人名><體積>大</體積><食物>雞排</食物>'
        self.example_sentence = 'Kelly喜歡小白魔性的笑聲和吃豪大大雞排'

    def test_remove_annotation(self):
        result = remove_annotation(
            annotated_sentence=self.example_annotated_sentence,
        )
        self.assertEqual(
            self.example_sentence,
            result,
        )
        result = remove_annotation(
            annotated_sentence='Alvin亂入',
        )
        self.assertEqual(
            'Alvin亂入',
            result,
        )

    def test_transform_annotated_sentence_to_entity_object_with_clean_sentence(self):
        result = transform_annotated_sentence_to_entity_object(
            annotated_sentence=self.example_annotated_sentence,
            clean_sentence=self.example_sentence,
            entity2replacements=None,
        )
        self.assertEqual(
            [
                Entity(name='人名', start=0, end=5, value='Kelly'),
                Entity(name='人名', start=7, end=9, value='小白'),
                Entity(name='人名', start=16, end=18, value='豪大'),
                Entity(name='體積', start=18, end=19, value='大'),
                Entity(name='食物', start=19, end=21, value='雞排'),
            ],
            result,
        )
        result = transform_annotated_sentence_to_entity_object(
            annotated_sentence=self.example_annotated_sentence,
            clean_sentence=self.example_sentence,
            entity2replacements={
                '人名': ['CPH', 'Alvin', 'GB'],
                '體積': ['中', '小'],
                '食物': ['鵝肉便當', '叉燒飯', '牛肉麵'],
            },
        )
        self.assertEqual(
            [
                Entity(name='人名', start=0, end=5, value='Kelly',
                       replacements=['CPH', 'Alvin', 'GB']),
                Entity(name='人名', start=7, end=9, value='小白',
                       replacements=['CPH', 'Alvin', 'GB']),
                Entity(name='人名', start=16, end=18, value='豪大',
                       replacements=['CPH', 'Alvin', 'GB']),
                Entity(name='體積', start=18, end=19,
                       value='大', replacements=['中', '小']),
                Entity(name='食物', start=19, end=21, value='雞排',
                       replacements=['鵝肉便當', '叉燒飯', '牛肉麵']),
            ],
            result,
        )

        result = transform_annotated_sentence_to_entity_object(
            annotated_sentence='Alvin亂入',
            clean_sentence='Alvin亂入',
            entity2replacements=None,
        )
        self.assertEqual([], result)

    def test_transform_annotated_sentence_to_entity_object_with_wrong_clean_sentence(self):
        with self.assertRaises(ValueError):
            transform_annotated_sentence_to_entity_object(
                annotated_sentence=self.example_annotated_sentence,
                clean_sentence='Kelly喜歡小白魔性的笑聲和喝珍奶',
                entity2replacements=None,
            )

    def test_transform_annotated_sentence_to_datum(self):
        result = transform_annotated_sentence_to_datum(
            annotated_sentence=self.example_annotated_sentence,
            intents=['A', 'B', 'C'],
            entity2replacements=None,
        )
        self.assertEqual(
            Datum(
                utterance=self.example_sentence,
                intents=[Intent('A'), Intent('B'), Intent('C')],
                entities=[
                    Entity(name='人名', start=0, end=5, value='Kelly'),
                    Entity(name='人名', start=7, end=9, value='小白'),
                    Entity(name='人名', start=16, end=18, value='豪大'),
                    Entity(name='體積', start=18, end=19, value='大'),
                    Entity(name='食物', start=19, end=21, value='雞排'),
                ],
            ),
            result,
        )

        result = transform_annotated_sentence_to_datum(
            annotated_sentence='Alvin亂入',
            intents=['A', 'B', 'C'],
            entity2replacements=None,
        )
        self.assertEqual(
            Datum(
                utterance='Alvin亂入',
                intents=[Intent('A'), Intent('B'), Intent('C')],
                entities=None,
            ),
            result,
        )

    def test_transform_annotated_sentences_to_data_with_intents(self):
        result = transform_annotated_sentences_to_data(
            annotated_sentences=[
                '<brand>大塊</brand><food>牛肉麵</food>好吃',
                '蔣勤彥的瀏海好長',
            ],
            intents=[['preference', 'food'], None],
            entity2replacements=None,
        )
        self.assertEqual(
            [
                Datum(
                    utterance='大塊牛肉麵好吃',
                    intents=[Intent('preference'), Intent('food')],
                    entities=[
                        Entity(name='brand', start=0, end=2, value='大塊'),
                        Entity(name='food', start=2, end=5, value='牛肉麵'),
                    ],
                ),
                Datum(
                    utterance='蔣勤彥的瀏海好長',
                    intents=None,
                    entities=None,
                ),
            ],
            result,
        )

    def test_transform_annotated_sentences_to_data_without_intents(self):
        result = transform_annotated_sentences_to_data(
            annotated_sentences=[
                '<brand>大塊</brand><food>牛肉麵</food>好吃',
                '蔣勤彥的瀏海好長',
            ],
            intents=None,
            entity2replacements=None,
        )
        self.assertEqual(
            [
                Datum(
                    utterance='大塊牛肉麵好吃',
                    intents=None,
                    entities=[
                        Entity(name='brand', start=0, end=2, value='大塊'),
                        Entity(name='food', start=2, end=5, value='牛肉麵'),
                    ],
                ),
                Datum(
                    utterance='蔣勤彥的瀏海好長',
                    intents=None,
                    entities=None,
                ),
            ],
            result,
        )
