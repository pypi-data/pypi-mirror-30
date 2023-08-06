from unittest import TestCase

from ..expand_by_entities import (
    expand_by_entities,
    partition_by_entities,
    augment_single_partition_utterances,
    augment_single_partition_utterances_with_upper_bound,
)
from ..elements import (
    Datum,
    Entity,
    Intent,
)


class ExpandByEntitiesTestCase(TestCase):

    def setUp(self):
        self.utterance = '我想訂明天從紐約飛到新加坡的機票'
        self.entities = [
            Entity(name='日期', value='明天', start=3, end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
            Entity(name='目的地', value='新加坡', start=10, end=13, replacements=['斯堪地那維亞', 'KIX']),
        ]
        self.intents = [
            Intent(name='訂機票'),
        ]
        self.datum = Datum(
            utterance=self.utterance,
            intents=self.intents,
            entities=self.entities,
        )

        self.expected_utterances = [
            '我想訂明天從紐約飛到新加坡的機票',
            '我想訂下禮拜二從紐約飛到新加坡的機票',
            '我想訂明天從紐約飛到斯堪地那維亞的機票',
            '我想訂下禮拜二從紐約飛到斯堪地那維亞的機票',
            '我想訂明天從紐約飛到KIX的機票',
            '我想訂下禮拜二從紐約飛到KIX的機票',
        ]
        self.expected_entity_lists = [
            [
                Entity(name='日期', value='明天', start=3, end=5, replacements=['下禮拜二']),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='新加坡', start=10, end=13, replacements=['斯堪地那維亞', 'KIX']),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7, replacements=['明天']),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='新加坡', start=12, end=15, replacements=['斯堪地那維亞', 'KIX']),
            ],
            [
                Entity(name='日期', value='明天', start=3, end=5, replacements=['下禮拜二']),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='斯堪地那維亞', start=10, end=16, replacements=['新加坡', 'KIX']),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7, replacements=['明天']),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='斯堪地那維亞', start=12, end=18, replacements=['新加坡', 'KIX']),
            ],
            [
                Entity(name='日期', value='明天', start=3, end=5, replacements=['下禮拜二']),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='KIX', start=10, end=13, replacements=['斯堪地那維亞', '新加坡']),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7, replacements=['明天']),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='KIX', start=12, end=15, replacements=['新加坡', '斯堪地那維亞']),
            ],
        ]
        self.expected_entity_wo_replacements_lists = [
            [
                Entity(name='日期', value='明天', start=3, end=5),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='新加坡', start=10, end=13),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='新加坡', start=12, end=15),
            ],
            [
                Entity(name='日期', value='明天', start=3, end=5),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='斯堪地那維亞', start=10, end=16),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='斯堪地那維亞', start=12, end=18),
            ],
            [
                Entity(name='日期', value='明天', start=3, end=5),
                Entity(name='出發地', value='紐約', start=6, end=8),
                Entity(name='目的地', value='KIX', start=10, end=13),
            ],
            [
                Entity(name='日期', value='下禮拜二', start=3, end=7),
                Entity(name='出發地', value='紐約', start=8, end=10),
                Entity(name='目的地', value='KIX', start=12, end=15),
            ],
        ]
        self.expected_intents = [
            [Intent(name='訂機票')],
            [Intent(name='訂機票')],
            [Intent(name='訂機票')],
            [Intent(name='訂機票')],
            [Intent(name='訂機票')],
            [Intent(name='訂機票')],
        ]
        self.expected_data = []
        self.expected_data_without_replacement = []
        for utt, ents, ents_wo_re, ints in zip(
                self.expected_utterances,
                self.expected_entity_lists,
                self.expected_entity_wo_replacements_lists,
                self.expected_intents,
            ):
            self.expected_data.append(Datum(
                utterance=utt,
                entities=ents,
                intents=ints,
            ))
            self.expected_data_without_replacement.append(Datum(
                utterance=utt,
                entities=ents_wo_re,
                intents=ints,
            ))

    def test_correct_result_original_augmentation_method(self):
        result = expand_by_entities(
            self.datum,
            augment_method=augment_single_partition_utterances,
            include_replacements=True,
        )

        # correct expand numbers
        self.assertEqual(6, len(result))
        for idx, datum in enumerate(result):
            with self.subTest(datum_idx=idx):
                self.assertIn(datum, self.expected_data)

    def test_correct_result_augmentation_with_upper_bound(self):
        result = expand_by_entities(
            self.datum,
            augment_method=augment_single_partition_utterances_with_upper_bound,
            augment_params={"upper_bound": 50},
            include_replacements=True,
        )

        # correct expand numbers
        self.assertEqual(6, len(result))
        for idx, datum in enumerate(result):
            with self.subTest(datum_idx=idx):
                self.assertIn(datum, self.expected_data)

    def test_correct_result_wo_replacement(self):
        result = expand_by_entities(
            self.datum,
            augment_method=augment_single_partition_utterances,
            include_replacements=False,
        )

        # correct expand numbers
        self.assertEqual(6, len(result))
        for idx, datum in enumerate(result):
            with self.subTest(datum_idx=idx):
                self.assertIn(datum, self.expected_data_without_replacement)

    def test_partition_by_entities(self):
        entities, parts = partition_by_entities(self.datum)
        self.assertEqual(
            parts,
            ['我想訂', '明天', '從', '紐約', '飛到', '新加坡', '的機票'],
        )
