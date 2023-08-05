from unittest import TestCase

from ..elements import (
    Intent,
    Entity,
    Datum,
)
from ..exceptions import (
    EntityOverlapping,
    EntityPositionError,
)


class ElementIntentTestCase(TestCase):

    def test_init(self):
        intent_name = 'INTENT1'
        intent = Intent(intent_name)
        self.assertEqual(intent.name, intent_name)


class ElementEntityTestCase(TestCase):

    def test_no_replacements(self):
        ent = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
        )
        self.assertTrue(ent.no_replacements())

    def test_has_replacements(self):
        ent = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        self.assertFalse(ent.no_replacements())

    def test_from_dict(self):
        name = 'LOC'
        start = 1
        end = 2
        replacements = ['斯堪地那維亞', 'KIX']
        utterance = '去紐約的機票'
        entity = {
            'name': name,
            'start': start,
            'end': end,
            'replacements': replacements,
        }
        ent = Entity.from_dict(entity, utterance)
        self.assertIsInstance(ent, Entity)
        self.assertEqual(ent.value, '紐約')
        self.assertEqual(ent.name, 'LOC')
        self.assertEqual(ent.start, start)
        self.assertEqual(ent.end, end + 1)
        self.assertEqual(ent.replacements, set(replacements))

    def test_from_dict_no_replacements(self):
        name = 'LOC'
        start = 1
        end = 2
        utterance = '去紐約的機票'
        entity = {
            'name': name,
            'start': start,
            'end': end,
        }
        ent = Entity.from_dict(entity, utterance)
        self.assertIsInstance(ent, Entity)
        self.assertEqual(ent.value, '紐約')
        self.assertEqual(ent.name, 'LOC')
        self.assertEqual(ent.start, start)
        self.assertEqual(ent.end, end + 1)
        self.assertEqual(ent.replacements, set([]))

    def test_to_dict(self):
        name = 'LOC'
        start = 1
        end = 2
        replacements = ['斯堪地那維亞', 'KIX']
        entity = {
            'name': name,
            'start': start,
            'end': end,
            'replacements': replacements,
        }
        ent = Entity(
            name=name,
            value='紐約',
            start=start,
            end=end + 1,
            replacements=replacements,
        )
        ent_tx = ent.to_dict()
        self.assertEqual(ent_tx['name'], entity['name'])
        self.assertEqual(ent_tx['start'], entity['start'])
        self.assertEqual(ent_tx['end'], entity['end'])
        self.assertEqual(set(ent_tx['replacements']),
                         set(entity['replacements']))

    def test_to_dict_no_replacement(self):
        name = 'LOC'
        start = 1
        end = 2
        entity = {
            'name': name,
            'start': start,
            'end': end,
        }
        ent = Entity(
            name=name,
            value='紐約',
            start=start,
            end=end + 1,
        )
        ent_tx = ent.to_dict()
        self.assertEqual(ent_tx['name'], entity['name'])
        self.assertEqual(ent_tx['start'], entity['start'])
        self.assertEqual(ent_tx['end'], entity['end'])
        self.assertNotIn('replacements', ent_tx)

    def test_equal(self):
        ent1 = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent2 = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        self.assertEqual(ent1, ent2)

    def test_not_equal(self):
        ent = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_name = Entity(
            name='LOC_2',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_value = Entity(
            name='LOC',
            value='新加坡',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_start = Entity(
            name='LOC',
            value='紐約',
            start=0,
            end=2,
            replacements=['台北'],
        )
        ent_diff_end = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=3,
            replacements=['台北'],
        )
        ent_diff_replacements = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北', 'KIX'],
        )
        self.assertNotEqual(ent, ent_diff_name)
        self.assertNotEqual(ent, ent_diff_value)
        self.assertNotEqual(ent, ent_diff_start)
        self.assertNotEqual(ent, ent_diff_end)
        self.assertNotEqual(ent, ent_diff_replacements)

    def test_raise_error_if_compare_different_type(self):
        ent = Entity(
            name='LOC',
            value='紐約',
            start=1,
            end=2,
            replacements=['台北'],
        )
        ent_diff_type = object()
        with self.assertRaises(TypeError):
            ent == ent_diff_type


class ElementDatumTestCase(TestCase):

    def test_raise_entity_position_error_if_entity_position_wrong(self):
        with self.subTest(case='wrong end'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐約的機票',
                    intents=[Intent('查機票')],
                    entities=[
                        Entity(name='LOC', value='紐約', start=1, end=2),
                    ],
                )
        with self.subTest(case='wrong start'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐約的機票',
                    intents=[Intent('查機票')],
                    entities=[
                        Entity(name='LOC', value='紐約', start=0, end=3),
                    ],
                )
        with self.subTest(case='wrong value'):
            with self.assertRaises(EntityPositionError):
                Datum(
                    utterance='去紐曰的機票',
                    intents=[Intent('查機票')],
                    entities=[
                        Entity(name='LOC', value='紐約', start=1, end=3),
                    ],
                )

    def test_raise_entity_overlap_if_entity_overlaps(self):
        with self.assertRaises(EntityOverlapping):
            Datum(
                utterance='我想吃麥當勞快樂兒童餐',
                intents=[Intent('查機票')],
                entities=[
                    Entity(name='FEELING', value='快樂', start=6, end=8),
                    Entity(name='SUIT', value='快樂兒童餐', start=6, end=11),
                ],
            )

    def test_entities_correct_order_in_datum(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        entities = [
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(name='訂機票'),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )

        expected_entities = [
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
        ]
        for result_entity, expected_entity in zip(datum.entities, expected_entities):
            self.assertEqual(result_entity.name, expected_entity.name)
            self.assertEqual(result_entity.value, expected_entity.value)
            self.assertEqual(result_entity.start, expected_entity.start)
            self.assertEqual(result_entity.end, expected_entity.end)

    def test_has_entities(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent('查機票')],
            entities=[
                Entity(name='LOC', value='紐約', start=1, end=3),
            ],
        )
        self.assertTrue(datum.has_entities())

    def test_has_no_entities(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent('查機票')],
            entities=[],
        )
        self.assertFalse(datum.has_entities())

    def test_has_intents(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=[Intent('查機票')],
            entities=[
                Entity(name='LOC', value='紐約', start=1, end=3),
            ],
        )
        self.assertTrue(datum.has_intents())

    def test_has_no_intents(self):
        datum = Datum(
            utterance='去紐約的機票',
            intents=None,
            entities=[
                Entity(name='LOC', value='紐約', start=1, end=3),
            ],
        )
        self.assertFalse(datum.has_intents())

    def test_same_utterance(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        entities = [
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(name='訂機票'),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance,
        )
        self.assertTrue(datum.has_same_utterance_as(datum2))

    def test_same_intents(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        utterance2 = '我想訂機票'
        entities = [
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(name='訂機票'),
        ]
        intents2 = [
            Intent(name='訂機票'),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance2,
            intents=intents2,
        )
        self.assertTrue(datum.has_same_intents_as(datum2))

    def test_same_entities(self):
        utterance = '我想訂明天從紐約飛到新加坡的機票'
        utterance2 = '我想查明天從紐約飛往新加坡的機票'
        entities = [
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
        ]
        entities2 = [
            Entity(name='目的地', value='新加坡', start=10,
                   end=13, replacements=['斯堪地那維亞', 'KIX']),
            Entity(name='日期', value='明天', start=3,
                   end=5, replacements=['下禮拜二']),
            Entity(name='出發地', value='紐約', start=6, end=8),
        ]
        intents = [
            Intent(name='訂機票'),
        ]
        intents2 = [
            Intent(name='查機票'),
        ]
        datum = Datum(
            utterance=utterance,
            intents=intents,
            entities=entities,
        )
        datum2 = Datum(
            utterance=utterance2,
            intents=intents2,
            entities=entities2,
        )
        self.assertTrue(datum.has_same_entities_as(datum2))

    def test_load_from_legacy_multi_intents(self):
        result = Datum.from_dict(
            utterance_obj={
                'utterance': '豆漿很好喝, 但打不出奶泡',
                'intent': {'names': ['preference', 'guidance']},
            },
        )
        self.assertEqual(
            Datum(
                utterance='豆漿很好喝, 但打不出奶泡',
                intents=[Intent('preference'), Intent('guidance')],
            ),
            result,
        )

    def test_to_dict(self):
        utterance = "我想訂明天從紐約飛到新加坡的機票"
        intent_names = ['preference', 'guidance']
        entity_name = '目的地'
        entity_start = 10
        entity_end = 13
        entity_replacements = ['斯堪地那維亞', 'KIX']
        expected = {
            'utterance': utterance,
            'intent': {'names': intent_names},
            'entities': [
                {
                    'name': entity_name,
                    'start': entity_start,
                    'end': entity_end - 1,
                    'replacements': entity_replacements,
                },
            ],
        }
        entity = Entity(
            name=entity_name,
            value='新加坡',
            start=entity_start,
            end=entity_end,
            replacements=entity_replacements,
        )
        actual = Datum(
            utterance=utterance,
            intents=[Intent(name=name) for name in intent_names],
            entities=[entity],
        ).to_dict()
        self.assertEqual(
            Datum.from_dict(expected),
            Datum.from_dict(actual),
        )

    def test_to_dict_without_entities(self):
        utterance = "我想訂明天從紐約飛到新加坡的機票"
        intent_names = ['preference', 'guidance']

        expected = {
            'utterance': utterance,
            'intent': {'names': intent_names},
        }
        actual = Datum(
            utterance=utterance,
            intents=[Intent(name=name) for name in intent_names],
            entities=[],
        ).to_dict()
        self.assertEqual(
            Datum.from_dict(expected),
            Datum.from_dict(actual),
        )

    def test_to_dict_without_intents(self):
        utterance = "我想訂明天從紐約飛到新加坡的機票"
        entity_name = '目的地'
        entity_start = 10
        entity_end = 13
        entity_replacements = ['斯堪地那維亞', 'KIX']
        expected = {
            'utterance': utterance,
            'intent': {'names': []},
            'entities': [
                {
                    'name': entity_name,
                    'start': entity_start,
                    'end': entity_end - 1,
                    'replacements': entity_replacements,
                },
            ],
        }
        entity = Entity(
            name=entity_name,
            value='新加坡',
            start=entity_start,
            end=entity_end,
            replacements=entity_replacements,
        )
        actual = Datum(
            utterance=utterance,
            intents=[],
            entities=[entity],
        ).to_dict()
        self.assertEqual(
            Datum.from_dict(expected),
            Datum.from_dict(actual),
        )
