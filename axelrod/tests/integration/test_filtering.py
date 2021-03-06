import unittest

from axelrod import filtered_strategies, seed, short_run_time_strategies
from axelrod.tests.property import strategy_lists
from hypothesis import example, given, settings
from hypothesis.strategies import integers


class TestFiltersAgainstComprehensions(unittest.TestCase):
    """
    Test that the results of filtering strategies via a filterset dict
    match the results from using a list comprehension.
    """

    @given(strategies=strategy_lists(min_size=20, max_size=20))
    def test_boolean_filtering(self, strategies):

        classifiers = [
            "stochastic",
            "long_run_time",
            "manipulates_state",
            "manipulates_source",
            "inspects_source",
        ]

        for classifier in classifiers:
            comprehension = set([s for s in strategies if s.classifier[classifier]])
            filterset = {classifier: True}
        filtered = set(filtered_strategies(filterset, strategies=strategies))
        self.assertEqual(comprehension, filtered)

    @given(
        min_memory_depth=integers(min_value=1, max_value=10),
        max_memory_depth=integers(min_value=1, max_value=10),
        memory_depth=integers(min_value=1, max_value=10),
        strategies=strategy_lists(min_size=20, max_size=20),
    )
    @example(
        min_memory_depth=float("inf"),
        max_memory_depth=float("inf"),
        memory_depth=float("inf"),
        strategies=short_run_time_strategies,
    )
    @settings(max_examples=5)
    def test_memory_depth_filtering(
        self, min_memory_depth, max_memory_depth, memory_depth,
        strategies
    ):

        min_comprehension = set(
            [
                s
                for s in strategies
                if s().classifier["memory_depth"] >= min_memory_depth
            ]
        )
        min_filterset = {"min_memory_depth": min_memory_depth}
        min_filtered = set(filtered_strategies(min_filterset,
                                               strategies=strategies))
        self.assertEqual(min_comprehension, min_filtered)

        max_comprehension = set(
            [
                s
                for s in strategies
                if s().classifier["memory_depth"] <= max_memory_depth
            ]
        )
        max_filterset = {"max_memory_depth": max_memory_depth}
        max_filtered = set(filtered_strategies(max_filterset,
                                               strategies=strategies))
        self.assertEqual(max_comprehension, max_filtered)

        comprehension = set(
            [
                s
                for s in strategies
                if s().classifier["memory_depth"] == memory_depth
            ]
        )
        filterset = {"memory_depth": memory_depth}
        filtered = set(filtered_strategies(filterset, strategies=strategies))
        self.assertEqual(comprehension, filtered)

    @given(seed_=integers(min_value=0, max_value=4294967295),
           strategies=strategy_lists(min_size=20, max_size=20),
           )
    @settings(max_examples=5)
    def test_makes_use_of_filtering(self, seed_, strategies):
        """
        Test equivalent filtering using two approaches.

        This needs to be seeded as some players classification is random.
        """
        classifiers = [["game"], ["length"], ["game", "length"]]

        for classifier in classifiers:
            seed(seed_)
            comprehension = set(
                [
                    s
                    for s in strategies
                    if set(classifier).issubset(set(s().classifier["makes_use_of"]))
                ]
            )

            seed(seed_)
            filterset = {"makes_use_of": classifier}
            filtered = set(filtered_strategies(filterset, strategies=strategies))

            self.assertEqual(
                comprehension, filtered, msg="classifier: {}".format(classifier)
            )
