.. |travis| image:: https://api.travis-ci.org/samirelanduk/points.svg?branch=0.4

.. _travis https://travis-ci.org/samirelanduk/points/

.. |coveralls| image:: https://coveralls.io/repos/github/samirelanduk/points/badge.svg?branch=0.4

.. _coveralls https://coveralls.io/github/samirelanduk/points/

.. |pypi| image:: https://img.shields.io/pypi/pyversions/points.svg


|travis|_ |coveralls|_ |pypi|

points
======

points is a Python library for performing linear algebra and geometry
calculations.

Example
-------

  >>> import points
  >>> vector = points.Vector(4, 3, 12)
  >>> vector.magnitude()
  >>> 13.0





Installing
----------

pip
~~~

points can be installed using pip:

``$ pip3 install points``

points is written for Python 3, and does not support Python 2. It is tested on
Python 3.5 and above.

If you get permission errors, try using ``sudo``:

``$ sudo pip3 install points``


Development
~~~~~~~~~~~

The repository for points, containing the most recent iteration, can be
found `here <http://github.com/samirelanduk/points/>`_. To clone the
points repository directly from there, use:

``$ git clone git://github.com/samirelanduk/points.git``


Requirements
~~~~~~~~~~~~

points has no dependencies, compiled or otherwise, and is pure Python.


Overview
--------

points is a library for performing geometry and linear algebra calculations.

Linear Algebra
~~~~~~~~~~~~~~

Vectors
#######

The ``Vector`` is the simplest linear algebra object. They can
represent a point in space, or the attributes of an object.

  >>> import points
  >>> vector = points.Vector(4, 3, 12)
  >>> vector.values()
  (4, 3, 12)
  >>> vector[2]
  12
  >>> vector.length()
  3

Note that 'length' here refers to the number of values in the Vector - to get the
size of the line the Vector represents in space, you need the magnitude:

  >>> vector.magnitude()
  13.0

You can get the component vectors like so:

  >>> vector.components()
  (<Vector [4, 0, 0]>, <Vector [0, 3, 0]>, <Vector [0, 0, 12]>)

You can add and remove values to the Vector in the same way you would with a
``list``:

  >>> vector.add(17)
  >>> vector.values()
  (4, 3, 12, 17)
  >>> vector.remove(17)
  >>> vector.values()
  (4, 3, 12)
  >>> vector.insert(1, 9)
  >>> vector.values()
  (4, 9, 3, 12)
  >>> vector.pop(1)
  9
  >>> vector.values()
  (4, 3, 12)

Vectors can be multiplied by scalar values (numbers) to get new Vectors:

  >>> vector * 5
  <Vector [20, 15, 60]>

Vectors can also be combined with other Vectors, with basic arithmetic, and also
with the dot product and angle between them:

  >>> vector2 = points.Vector(9, -1, 4)
  >>> vector + vector2
  <Vector [13, 2, 16]>
  >>> vector - vector2
  <Vector [-5, 4, 8]>
  >>> vector.distance_to(vector2)
  10.246950765959598
  >>> vector.dot(vector2)
  81
  >>> vector.cross(vector2)
  <Vector [24, 92, -31]>
  >>> vector.angle_with(vector2)
  0.8900119515744306
  >>> vector.angle_with(vector2, degrees=True)
  50.99392854141668

A Vector's 'span' is the set of all Vectors which can be created by scaling it,
and the span of a set of Vectors is all the Vectors which can be created from
linear combinations of those Vectors. A set of vectors are linearly independent
if none of them are in the span of the others...

  >>> span = vector.span()
  >>> vector in span
  True
  >>> vector2 in span
  False
  >>> span = vector.span_with(vector2)
  >>> vector in span
  True
  >>> vector2 in span
  True
  >>> points.Vector(1, 2, 3) in span
  True
  >>> vector.linearly_independent_of(vector2)
  True


Matrices
########

A Matrix is a rectangular array of numbers, often used to represent linear
transformations. They are created by passing in rows:

  >>> matrix = points.Matrix([1, 2, 3], [4, 5, 6])
  >>> matrix.rows()
  ((1, 2, 3), (4, 5, 6))
  >>> matrix.columns()
  ((1, 4), (2, 5), (3, 6))

You can also pass it vector, which will be interpreted as **columns**:

  >>> col1 = points.Vector(1, 4, 7)
  >>> col2 = points.Vector(2, 5, 8)
  >>> col3 = points.Vector(3, 6, 9)
  >>> matrix2 = points.Matrix(col1, col2, col3)
  >>> matrix2.rows()
  ((1, 2, 3), (4, 5, 6), (7, 8, 9))
  >>> matrix2.columns()
  ((1, 4, 7), (2, 5, 8), (3, 6, 9))

You can add matrices together with ``+`` or multiply them by scalars with ``*``.
The ``@`` operator is used to multiply a Matrix with another Matrix, or with a
Vector.

Matrices currently support the concepts of inversion, adjoin, cofactors, minors,
determinants, transposition, Gaussian elimination, and checks for row echelon
form and reduced row echelon form. See the full documentation for more details.


Changelog
---------

Release 0.4.0
~~~~~~~~~~~~~

`2 April 2018`

* Fixed rotation matrices.
* Added matrix cofactors and minors.
* Added matrix transposition and adjoint matrices.
* Added matrix determinants.
* Added matrix inversion.
* Implemented vector spans with its own class.
* Added vector linear dependence checks.
* Added matrix column space and rank.
* Overhauled geometry tools.
* Added aligning of vectors to axes.


Release 0.3.0
~~~~~~~~~~~~~

`31 October 2017`

* Added Matrix class.
* Added Matrix-Vector multiplication.
* Implemented CI.


Release 0.2.0
~~~~~~~~~~~~~

`10 October 2017`

* Added Vector distances.
* Added component Vector generation.
* Added Vector cross product.


Release 0.1.0
~~~~~~~~~~~~~

`9 September 2017`

* Added basic Vector class.
* Added basic degrees/radians conversion decorator.
