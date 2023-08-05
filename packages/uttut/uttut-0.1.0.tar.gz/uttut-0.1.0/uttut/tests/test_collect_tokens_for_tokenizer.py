# -*- coding: utf-8 -*-
from unittest import TestCase

from ..elements import (
    Entity,
    Datum,
)
from ..collect_tokens_for_tokenizer import (
    collect_tokens_for_tokenizer,
    longest_common_substring,
    get_tokens_from_replacements,
)


class CollectTokensForTokenizerTestCase(TestCase):

    def setUp(self):
        self.data = [
            Datum(
                utterance='新興國家固定收益基金賺錢嗎？',
                entities=[
                    Entity(
                        start=0,
                        end=10,
                        name='基金名稱',
                        value='新興國家固定收益基金',
                        replacements=['全球債券基金',
                                      '富蘭克林坦伯頓成長基金',
                                      '富蘭克林坦伯頓中小型公司成長基金',
                                      '富蘭克林成長基金',
                                      '富蘭克林黃金基金',
                                      '富蘭克林公用事業基金',
                                      '富蘭克林高科技基金',
                                      '吉富世界基金-歐元累積',
                                      '吉富世界基金-美元累積',
                                      '富蘭克林坦伯頓法人機構專用基金',
                                      '富蘭克林坦伯頓全球基金',
                                      '富蘭克林坦伯頓外國基金',
                                      '富蘭克林華美第一富基金',
                                      '富蘭克林華美坦伯頓全球股票組合基金',
                                      '富蘭克林華美新世界股票基金',
                                      '富蘭克林華美中華基金',
                                      '富蘭克林華美新興趨勢傘型基金之新興市場股票組合基金',
                                      '富蘭克林華美中國消費基金',
                                      '富蘭克林華美台股傘型基金之高科技基金',
                                      '富蘭克林華美台股傘型基金之傳產基金',
                                      '富蘭克林華美中國傘型基金之中國A股基金',
                                      '富蘭克林華美退休傘型之目標2037組合證券投資信託基金-台幣',
                                      '富蘭克林華美退休傘型之目標2047組合證券投資信託基金-台幣',
                                      '富蘭克林華美中國傘型基金之中國A股基金',
                                      '富蘭克林華美中國傘型基金之中國A股基金-美元計價',
                                      '中國基金',
                                      '潛力歐洲基金-美元避險',
                                      '全球核心策略基金',
                                      '新興國家基金',
                                      '新興市場',
                                      '新興債',
                                      ],
                    ),
                ],
            ),
        ]

    def test_collect_tokens_for_tokenizer(self):
        collect_tokens_for_tokenizer(self.data)

    def test_longest_common_substring(self):
        result = longest_common_substring(
            s1='gb喜歡吃拉麵',
            s2='鷹流拉麵很好吃',
        )
        self.assertEqual('拉麵', result)

    def test_get_tokens_from_replacements(self):
        result = get_tokens_from_replacements(
            data=[
                Datum(
                    utterance='AB',
                    entities=[
                        Entity(
                            name='1',
                            start=1,
                            end=2,
                            value='B',
                            replacements=['B1', 'B2', 'B3'],
                        ),
                    ],
                ),
                Datum(
                    utterance='CD',
                    entities=[
                        Entity(
                            name='2',
                            start=1,
                            end=2,
                            value='D',
                            replacements=['D1', 'D2', 'D3'],
                        ),
                    ],
                ),
                Datum(
                    utterance='CE',
                    entities=[
                        Entity(
                            name='2',
                            start=1,
                            end=2,
                            value='E',
                            replacements=['E1', 'E2', 'E3'],
                        ),
                    ],
                ),
            ],
        )
        self.assertEqual(
            set(['B1', 'B2', 'B3', 'D1', 'D2', 'D3']),
            result,
        )
