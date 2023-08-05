# ------------------------------------------------------------------------------
# Unittests
# ------------------------------------------------------------------------------
import sys
import os.path
from unittest import TestCase
from ls.sampleproject import SquareBuilder


class TestSquareBuilder(TestCase):
    def setUp(self):
        here = os.path.dirname(os.path.abspath(__file__))
        self.builder = SquareBuilder(os.path.join(here, "test.words"))

    def testMatchingWords(self):
        matchingWords = set(self.builder.matchingWords)
        self.assertEqual(len(matchingWords), len(self.builder.matchingWords))
        for word in self.builder.matchingWords:
            self.assertEqual(len(word), 6)
            drow = word[::-1]
            self.assertNotEqual(drow, word)
            self.assertIn(drow, matchingWords)

    def testSquares(self):
        for square in self.builder:
            self.assertIs(type(square), list)
            self.assertEqual(len(square), 6)
            for n in range(6):
                with self.subTest(row=n):
                    self.assertIs(type(square[n]), str)
                    self.assertEqual(len(square[n]), 6)
            row = lambda y: [c for c in square[y]]
            column = lambda x: [row[x] for row in square]
            for n in range(6):
                with self.subTest(n=n):
                    self.assertEqual(row(n), column(n))
            self.assertEqual(row(0), row(5)[::-1])
            self.assertEqual(row(1), row(4)[::-1])
            self.assertEqual(row(2), row(3)[::-1])
            self.assertEqual(column(0), column(5)[::-1])
            self.assertEqual(column(1), column(4)[::-1])
            self.assertEqual(column(2), column(3)[::-1])
