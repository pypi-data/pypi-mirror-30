=========
reflowrst
=========

Installation
============

>>> sudo pip install reflowrst

Usage
=====

Example:

>>> from reflowrst import reflow
>>> text = 'Here is a paragraph that is far too long and will need to wrap.'
>>> print(reflow(text, 47))
Here is a paragraph that is far too long and
will need to wrap.

You can also get the longest possible form of the rst text by using 0
for the space. For example:

>>> paragraph = '''Here is a paragraph that is far too long and
will need to wrap.'''
>>> print(reflow(paragraph, 0))
Here is a paragraph that is far too long and will need to wrap.

Todo
====
* |+| Titles
* |+| Transitions
* |+| Paragraphs
* |+| Bullet Lists
* |+| Enumerated Lists
* |+| Definitions
* |+| Fields
* |+| Options
* |+| Literal Blocks
* |-| Quoted Literal Blocks
* |+| Line Blocks
* |+| Block Quotes
* |-| Doctest Blocks
* |+| Grid Tables
* |+| Simple Tables
* |+| Footnotes
* |+| Citations
* |+| Directives

.. |+| unicode:: U+2611
.. |-| unicode:: U+2610
