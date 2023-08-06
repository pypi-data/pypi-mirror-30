#############
Encase
#############

Encase - A Better Dictionary Class.

Features
************

The Encase class is used to create dictionary style objects
with:

* Attribute access via dot (.) notation
* Nested instances of itself
* Automatic resursive conversion for existing dictionaries, including nested lists of dictionaries

Installation
************
Install this package using pip:

``pip install encase``

Usage
************
Basic Usage:
::

    >>> from encase import Encase
    >>> d = Encase()
    >>> d.hello_world = "Hello World!"
    >>> print(d.hello_world)
    Hello World!

    >>> d.child = Encase()
    >>> d.child.message = "Encase Instances can be nested"
    >>> print(d.child.message)
    Encase Instances can be nested

Encase also has two methods, get(), and, set(), 

Examples
************
Create a JSON File:
::

    >>> import json
    >>> j = Encase()
    >>> j.data = Encase()
    >>> j.data.info = "JSON can be converted into nested Encases"
    >>> j.data.features = []
    >>> j.data.features.append('Resursively transform dictionaries into Encases')
    >>> j.data.features.append('Supports recursion through lists as well')
    >>> j.data.features.append(Encase())
    >>> j.data.features[2].example = "Example of a Encase in a list"

    >>> print(j)
    {
      'data': {
        'info': 'JSON can be converted into nested Encases',
        'features': [
          'Resursively transform dictionaries into Encases',
          'Supports recursion through lists as well',
          {
            'example': 'Example of a Encase in a list'
          }
        ]
      }
    }

    >>> with open('example.json', 'w') as stream:
    ...   json.dump(j, stream)

Read a JSON File:
::

    >>> with open('example.json', 'r') as stream:
    ...     j_data = json.load(stream)

    >>> j_stack = Encase(j_data)
    >>> print(j_stack.data.info)
    JSON can be converted into nested Encases

    >>> for item in j_stack.data.features:
    ...     print(item)
    ...
    Resursively transform dictionaries into Encases
    Supports recursion through lists as well
    {'example': 'Example of a Encase in a list'}

    >>> print(j_stack.data.features[2].example)
    Example of a Encase in a list

Author
************
* Ryan Miller - ryan@devopsmachine.com
