# -*- coding: utf-8 -*-
"""Test the tabulate output adapter."""

from __future__ import unicode_literals
from textwrap import dedent

from cli_helpers.tabular_output import tabulate_adapter


def test_tabulate_wrapper():
    """Test the *output_formatter.tabulate_wrapper()* function."""
    data = [['abc', 1], ['d', 456]]
    headers = ['letters', 'number']
    output = tabulate_adapter.adapter(iter(data), headers, table_format='psql')
    assert "\n".join(output) == dedent('''\
        +-----------+----------+
        | letters   |   number |
        |-----------+----------|
        | abc       |        1 |
        | d         |      456 |
        +-----------+----------+''')

    data = [['{1,2,3}', '{{1,2},{3,4}}', '{å,魚,текст}'], ['{}', '<null>', '{<null>}']]
    headers = ['bigint_array', 'nested_numeric_array', '配列']
    output = tabulate_adapter.adapter(iter(data), headers, table_format='psql')
    assert "\n".join(output) == dedent('''\
        +----------------+------------------------+--------------+
        | bigint_array   | nested_numeric_array   | 配列         |
        |----------------+------------------------+--------------|
        | {1,2,3}        | {{1,2},{3,4}}          | {å,魚,текст} |
        | {}             | <null>                 | {<null>}     |
        +----------------+------------------------+--------------+''')


def test_markup_format():
    """Test that markup formats do not have number align or string align."""
    data = [['abc', 1], ['d', 456]]
    headers = ['letters', 'number']
    output = tabulate_adapter.adapter(iter(data), headers, table_format='mediawiki')
    assert "\n".join(output) == dedent('''\
        {| class="wikitable" style="text-align: left;"
        |+ <!-- caption -->
        |-
        ! letters !! number
        |-
        | abc || 1
        |-
        | d || 456
        |}''')
