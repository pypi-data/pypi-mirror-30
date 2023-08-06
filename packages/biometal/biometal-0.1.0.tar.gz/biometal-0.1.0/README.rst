|travis| |coveralls| |pypi|

.. |travis| image:: https://api.travis-ci.org/samirelanduk/biometal.svg?branch=0.1
  :target: https://travis-ci.org/samirelanduk/biometal/

.. |coveralls| image:: https://coveralls.io/repos/github/samirelanduk/biometal/badge.svg?branch=0.1
  :target: https://coveralls.io/github/samirelanduk/biometal/

.. |pypi| image:: https://img.shields.io/pypi/pyversions/biometal.svg
  :target: https://pypi.org/project/biometal/

biometal
========

biometal is a suite of tools for dealing with metalloproteins.

Example
-------

  >>> import atomium
  >>> import biometal
  >>> model = atomium.fetch('1ton').model
  >>> zinc = model.atom(element='ZN')
  >>> biometal.hydrophobic_contrast(model, *zinc.location, 4)
  435.9691187500001





Installing
----------

pip
~~~

biometal can be installed using pip:

``$ pip3 install biometal``

biometal is written for Python 3, and does not support Python 2. It currently
requires Python 3.5 and above.

If you get permission errors, try using ``sudo``:

``$ sudo pip3 install biometal``


Development
~~~~~~~~~~~

The repository for biometal, containing the most recent iteration, can be
found `here <http://github.com/samirelanduk/biometal/>`_. To clone the
biometal repository directly from there, use:

``$ git clone git://github.com/samirelanduk/biometal.git``


Requirements
~~~~~~~~~~~~

biometal relies heavily on
`atomium <https://atomium.samireland.com/>`_  - pip will install this
automatically when it installs biometal.


Overview
--------

biometal analyses metalloproteins.

Hydrophobic Contrast
~~~~~~~~~~~~~~~~~~~~

biometal can implement the hydrophobic contrast function as implemented in
(1990) Where metal ions bind in proteins:

  >>> import atomium
  >>> import biometal
  >>> model = atomium.fetch('1ton').model
  >>> zinc = model.atom(element='ZN')
  >>> biometal.hydrophobic_contrast(model, *zinc.location, 4)
  435.9691187500001

This uses atomic solvation parameters to determine hydrophobicity. To use
the square of partial charge instead, use the ``pc=True`` argument.


Changelog
---------

Release 0.1.0
~~~~~~~~~~~~~

`17 April 2018`

* Started template generation.
* Implemented solvation measuring using solvation parameters.
* Implemented solvation measuring using partial charge.
* Implemented hydrophobic contrast function.
