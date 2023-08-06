# -*- coding: utf-8 -*-

"""
In computer science, a **queue** is a particular kind of abstract data.rst type or 
collection in which the entities in the collection are kept in order and the 
principal (or only) operations on the collection are the addition of entities 
to the rear terminal position, known as *enqueue*, and removal of entities from 
the front terminal position, known as dequeue. This makes the queue a 
First-In-First-Out (FIFO) data.rst structure. In a FIFO data.rst structure, the first 
element added to the queue will be the first one to be removed. This is equivalent 
to the requirement that once a new element is added, all elements that were added 
before have to be removed before the new element can be removed. Often a peek or 
front operation is also entered, returning the value of the front element without 
dequeuing it. A queue is an example of a linear data.rst structure, or more abstractly 
a sequential collection. [1]_

Queues provide services in computer science, transport, and operations research 
where various entities such as data.rst, objects, persons, or events are stored and 
held to be processed later. In these contexts, the queue performs the function of 
a buffer. [1]_

Queues are common in computer programs, where they are implemented as data.rst structures 
coupled with access routines, as an abstract data.rst structure or in object-oriented 
languages as classes. Common implementations are circular buffers and linked lists. [1]_

Pseudo Code: https://en.wikipedia.org/wiki/Queue_%28abstract_data_type%29


.. [1] https://en.wikipedia.org/wiki/Queue_(abstract_data_type)
"""


from collections import deque


class Queue(object):
    """Queue data structure.
    
    Queue is implemented by using ``collections.deque``, which is a double-ended queue 
    and supports adding and removing elements from either end. The more commonly used 
    stacks and queues are degenerate forms of deques, where the inputs and outputs are 
    restricted to a single end.
    
    """
    def __init__(self):
        self._queue = deque([])

    def add(self, value):
        """Add element as the last item in the Queue.

        Worst Case Complexity: :math:`O(1)`.
        
        Parameters
        ----------
        value : object
            object to append in the end.
        """
        self._queue.append(value)

    def pop(self):
        """Remove element from the front of the Queue and return it's value.

        Worst Case Complexity:  :math:`O(1)`.
        
        Returns
        -------
        object
            return the first object in the front of the Queue.
        """
        return self._queue.popleft()

    def is_empty(self):
        """Check whether the Queue is empty.
        
        Worst Case Complexity:  :math:`O(1)`.
        
        Returns
        -------
        bool
            Returns a boolean indicating if the Queue is empty.
        """
        return not len(self._queue)

    def size(self):
        """The size of the Queue.
        
        Worst Case Complexity:  :math:`O(1)`.
        
        Returns
        -------
        int
            Return size of the Queue.
        """
        return len(self._queue)
