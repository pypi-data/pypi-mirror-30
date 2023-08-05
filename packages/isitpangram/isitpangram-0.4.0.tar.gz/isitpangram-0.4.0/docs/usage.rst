=====
Usage
=====

To use IsItPangram in a project::

    >>> from isitpangram.isitpangram import is_pangram

    >>> is_pangram("the quick brown fox jumps over the lazy dog")
    True
    
    >>> is_pangram("the quick brown fox jumps over the lazy cat")
    False