# -*- coding: utf-8 -*-

import unittest

import pytest

from oujago.datatypes import Queue


class TestQueue(unittest.TestCase):
    @pytest.fixture()
    def test_queue(self):
        self.que = Queue()
        self.que.add(1)
        self.que.add(2)
        self.que.add(8)
        self.que.add(5)
        self.que.add(6)

        self.assertEqual(self.que.remove(), 1)
        self.assertEqual(self.que.size(), 4)
        self.assertEqual(self.que.remove(), 2)
        self.assertEqual(self.que.remove(), 8)
        self.assertEqual(self.que.remove(), 5)
        self.assertEqual(self.que.remove(), 6)
        self.assertEqual(self.que.is_empty(), True)



