"""
SortedSet
-------------

Implementation of Immutable Sorted Set collection.

You can get it by downloading it directly or by typing:

.. code:: bash

    $ pip install SortedSet

After it is installed you can start using it:

.. code:: bash

    $ SortedSet(['list_of_integer_data'])

For example

.. code:: bash

    $ SortedSet([1, 2, 5, 3, 3, 1])

Would return the following

.. code:: bash

    $ SortedSet([1, 2, 3, 5])

SortedSet Operations
-------------


Union
-------------

You can add two SortedSets together either by using '+' operator,
calling .union() method on one of the sets and providing the other,
or by using union operator '|'.

Take for example these two SortedSets

.. code:: bash

    $ a = SortedSet([1, 2, 5, 3])
    $ b = SortedSet([2, 4, 6])

We could add them together by running any of these commands

.. code:: bash

    $ a + b
    $ a.union(b)
    $ a | b

In all three cases the result would be the SortedSet

.. code:: bash

    $ SortedSet([1, 2, 3, 4, 5, 6])

Difference
-------------

You can subtract two SortedSets either calling .difference() method
on one of the sets and providing the other, or by using difference
operator '-'. Be aware that ordering of SortedSets matters.

Take for example the same two SortedSets we already used

.. code:: bash

    $ a = SortedSet([1, 2, 5, 3])
    $ b = SortedSet([2, 4, 6])

We can subtract them by running one of these two commands

.. code:: bash

    $ a - b
    $ a.difference(b)

In both cases the result would be the SortedSet

.. code:: bash

    $ SortedSet([1, 3, 5])

If we were to switch the order of the operands

.. code:: bash

    $ b - a
    $ b.difference(a)

We would get entirely different result

.. code:: bash

    $ SortedSet([4, 6])

Symmetric Difference
-------------

You can find unique members that are only contained in one of the
two SortedSets either by calling .symmetric_difference() method
on one of the sets and providing the other, or by using symmetric
difference operator '^'.

.. code:: bash

    $ a = SortedSet([1, 2, 5, 3])
    $ b = SortedSet([2, 4, 6])
    $ a.symmetric_difference(b)
    $ SortedSet([1, 3, 4, 5, 6])
    $ b ^ a
    $ SortedSet([1, 3, 4, 5, 6])

Intersection
-------------

You can find unique members that are contained in both of the
two SortedSets either by calling .intersection() method
on one of the sets and providing the other, or by using intersection
operator '&'.

.. code:: bash

    $ a = SortedSet([1, 2, 5, 3])
    $ b = SortedSet([2, 4, 6])
    $ a.intersection(b)
    $ SortedSet([2])
    $ b & a
    $ SortedSet([2])

Superset, Subset and Disjoint
-------------

It is also possible to check if one SortedSet is a superset
or subset of another either by using .issuperset() and
.issubset() methods or by using operators '>=' and '<='.


.. code:: bash

    $ a = SortedSet([1, 2])
    $ b = SortedSet([1, 2, 3])
    $ a.issuperset(b)
    $ False
    $ a >= b
    $ False
    $ a.issubset(b)
    $ True
    $ a <= b
    $ True

You can find out are two SortedSets disjoint, meaning that
they have no common members by running .isdisjoint() method
on one of the SortedSets.

.. code:: bash

    $ a = SortedSet([1, 3])
    $ b = SortedSet([6, 4, 8])
    $ a.isdisjoint(b)
    $ True
    $ a = SortedSet([4, 3])
    $ b = SortedSet([6, 4, 8])
    $ b.isdisjoint(a)
    $ False

Other operations
-------------

Other supported operations are:

len()
contains()
comparison of two SortedSets for equality or inequality
access to SortedSet members by their index


.. code:: bash

    $ a = SortedSet([1, 3, 7, 5])
    $ len(a)
    $ 4
    $ a.contains(1)
    $ True
    $ a.contains(31)
    $ False
    $ b = SortedSet([2, 3])
    $ a == b
    $ False
    $ c = SortedSet([3, 1, 5, 7])
    $ a == c
    $ True
    $ a != b
    $ True
    $ a[0]
    $ 1
    $ b[1]
    $ 3

"""

from setuptools import setup

setup(name='SortedSet',
      version='0.4',
      description='Implementation of Immutable Sorted Set collection',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/SortedSetCollection",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['SortedSet'],
      )

__author__ = 'Uros Jevremovic'