# -*- coding: utf-8 -*-

"""
In computer science, a stack is an abstract data type that serves as a collection of elements,
with two principal operations: push, which adds an element to the collection, and pop, which
removes the most recently added element that was not yet removed. The order in which elements
come off a stack gives rise to its alternative name, LIFO (for last in, first out). Additionally,
a peek operation may give access to the top without modifying the stack.


.. [1] https://en.wikipedia.org/wiki/Stack_(abstract_data_type)

"""


class Stack:
    """Stack data structure.

    The name "stack" for this type of structure comes from the analogy to a set of physical items
    stacked on top of each other, which makes it easy to take an item off the top of the stack,
    while getting to an item deeper in the stack may require taking off multiple other items first.

    """

    def __init__(self):
        self.stack_list = []

    def add(self, value):
        """Add element at last

        Time Complexity:  :math:`O(1)`
        """
        self.stack_list.append(value)

    def pop(self):
        """Remove element from last return value

        Time Complexity:  :math:`O(1)`
        """

        return self.stack_list.pop()

    def is_empty(self):
        """
        1 value returned on empty 0 value returned on not empty

        Time Complexity:  :math:`O(1)`
        """
        return not len(self.stack_list)

    def size(self):
        """
        Return size of stack

        Time Complexity:  :math:`O(1)`
        """
        return len(self.stack_list)