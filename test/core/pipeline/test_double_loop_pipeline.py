# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import logging

from haystack.components.others import Multiplexer
from haystack.core.pipeline import Pipeline
from haystack.testing.sample_components import Accumulate, AddFixedValue, Threshold

logging.basicConfig(level=logging.DEBUG)


def test_pipeline(tmp_path):
    accumulator = Accumulate()

    pipeline = Pipeline(max_loops_allowed=10)
    pipeline.add_component("add_one", AddFixedValue(add=1))
    pipeline.add_component("multiplexer", Multiplexer(type_=int))
    pipeline.add_component("below_10", Threshold(threshold=10))
    pipeline.add_component("below_5", Threshold(threshold=5))
    pipeline.add_component("add_three", AddFixedValue(add=3))
    pipeline.add_component("accumulator", accumulator)
    pipeline.add_component("add_two", AddFixedValue(add=2))

    pipeline.connect("add_one.result", "multiplexer")
    pipeline.connect("multiplexer.value", "below_10.value")
    pipeline.connect("below_10.below", "accumulator.value")
    pipeline.connect("accumulator.value", "below_5.value")
    pipeline.connect("below_5.above", "add_three.value")
    pipeline.connect("below_5.below", "multiplexer")
    pipeline.connect("add_three.result", "multiplexer")
    pipeline.connect("below_10.above", "add_two.value")

    pipeline.draw(tmp_path / "double_loop_pipeline.png")

    results = pipeline.run({"add_one": {"value": 3}})

    assert results == {"add_two": {"result": 13}}
    assert accumulator.state == 8
