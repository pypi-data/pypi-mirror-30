"""Contains the Matrix class."""

from fractions import Fraction
from .vectors import Vector, VectorSpan

class Matrix:
    """A Matrix is a rectangular array of numbers. They are created from
    iterables, which will be interpeted as rows unless specified otherwise.

    They can be added and subtracted from each other, and multiplied by a scalar
    using the `*` operator. To multiply a Matrix with another Matrix, use ``@``.

    :param iter args: The rows of the Matrix. Each row must be iterable.
    :raises ValueError: if you create an empty matrix.
    :raises TypeError: if you mix Vectors with other iterables.
    :raises TypeError: if you give non iterables.
    :raises ValueError: if you give rows of different lengths."""

    def __init__(self, *rows, columns=False):
        rows_ = []
        for row in rows:
            try:
                rows_.append(list(row))
            except TypeError:
                raise TypeError("{} is not iterable".format(row))
        if len(set(len(row) for row in rows_)) != 1:
            raise ValueError("Cannot make Matrix with unequal rows")
        if columns:
            rows_ = [[col[n] for col in rows_] for n in range(len(rows_[0]))]
        self._rows = rows_


    @staticmethod
    def identity(dimensions):
        """Creates an identity matrix.

        :param int dimensions: the size of the identity matrix to create.
        :raises TypeError: if non-integer dimension is given.
        :rtype: ``Matrix``"""

        if not isinstance(dimensions, int):
            raise TypeError("Dimensions must be int, not {}".format(dimensions))
        return Matrix(*[[
         1 if j == i else 0 for j in range(dimensions)
        ] for i in range(dimensions)])


    def __repr__(self):
        return "<{}×{} Matrix>".format(*self.size())


    def __str__(self):
        strings = [[str(val) for val in row] for row in self._rows]
        max_length = max([max([len(val) for val in row]) for row in strings])
        return "\n".join([
         " ".join([val.rjust(max_length) for val in row
        ]) for row in strings])


    def __contains__(self, item):
        for row in self._rows:
            if item in row:
                return True
        return False


    def __eq__(self, other):
        return isinstance(other, Matrix) and self._rows == other._rows


    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("{} is not a Matrix".format(other))
        if self.size() != other.size():
            raise ValueError("{} & {} are different sizes".format(self, other))
        return Matrix(*[[
         n1 + n2 for n1, n2 in zip(row1, row2)
        ] for row1, row2 in zip(self._rows, other._rows)])


    def __sub__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError("{} is not a Matrix".format(other))
        if self.size() != other.size():
            raise ValueError("{} & {} are different sizes".format(self, other))
        return Matrix(*[[
         n1 - n2 for n1, n2 in zip(row1, row2)
        ] for row1, row2 in zip(self._rows, other._rows)])


    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError(
             "{} isn't numeric - Matrix * operator needs scalars".format(other)
            )
        rows = [[n * other for n in row] for row in self._rows]
        return Matrix(*rows)


    def __rmul__(self, other):
        return self * other


    def __matmul__(self, other):
        if isinstance(other, Vector):
            if self.size()[1] != len(other):
                raise ValueError(
                 "{} and {} dimensions incompatible".format(self, other)
                )
            return Vector(*[sum(
             val * other.values()[i] for i, val in enumerate(row)
            ) for row in self._rows])
        if not isinstance(other, Matrix):
            raise TypeError("{} is not a Matrix".format(other))
        if self.size()[1] != other.size()[0]:
            raise ValueError(
             "{} and {} dimensions incompatible".format(self, other)
            )
        new_rows, other_columns = [], other.columns()
        for row in self._rows:
            new_row = []
            for c in range(len(other_columns)):
                new_row.append(sum([
                 row[j] * other._rows[j][c] for j in range(len(other._rows))
                ]))
            new_rows.append(new_row)
        return Matrix(*new_rows)


    def width(self):
        """Returns the Matrix width - how many columns it has.

        :rtype: ``int``"""

        return len(self._rows[0])


    def height(self):
        """Returns the Matrix height - how many rows it has.

        :rtype: ``int``"""

        return len(self._rows)


    def size(self):
        """Returns the dimensions of the Matrix.

        :rtype: ``tuple``"""

        return (self.height(), self.width())


    def rows(self):
        """Returns the rows of the Matrix.

        :rtype: ``tuple``"""

        return tuple([tuple(row) for row in self._rows])


    def columns(self):
        """Returns the rows of the Matrix.

        :rtype: ``tuple``"""

        return tuple([tuple([
         row[n] for row in self._rows
        ]) for n in range(len(self._rows[0]))])


    def is_square(self):
        """Checks if the number of rows equals the number of columns.

        :rtype: ``bool``"""

        return self.width() == self.height()


    def transposed(self):
        """Returns a transposed version of the matrix. The matrix calling the
        method is unaffected.

        :rtype: ``Matrix``"""

        return Matrix(*map(list, zip(*self._rows)))


    def minor(self, i, j):
        """Returns the first minor of the value at the position specified.

        :param int i: The row to use.
        :param int j: The column to use.
        :raises ValueError: if a non-square matrix is given.
        :rtype: ``float``"""

        if not self.is_square():
            raise ValueError("{} is not square".format(self))
        if self.width() == 2:
            return self._rows[1-i][1-j]
        return Matrix(*[[
         cell for c, cell in enumerate(row) if c != j
        ] for r, row in enumerate(self.rows()) if r != i]).determinant()


    def cofactor(self, i, j):
        """Returns the cofactor of the value at the position specified.

        :param int i: The row to use.
        :param int j: The column to use.
        :raises ValueError: if a non-square matrix is given.
        :rtype: ``float``"""

        return self.minor(i, j) * ((-1) ** (i + j))


    def minors(self):
        """Returns the matrix of minors for this matrix.

        :raises ValueError: if a non-square matrix is given.
        :rtype: ``Matrix``"""

        return Matrix(*[[
         self.minor(i, j) for j in range(len(row))
        ] for i, row in enumerate(self._rows)])


    def cofactors(self):
        """Returns the matrix of cofactors for this matrix.

        :raises ValueError: if a non-square matrix is given.
        :rtype: ``Matrix``"""

        return Matrix(*[[
         self.cofactor(i, j) for j in range(len(row))
        ] for i, row in enumerate(self._rows)])


    def determinant(self):
        """Returns the determinant of the matrix - the matrix must be square for
        this to happen.

        The Laplace expansion is used to calculate matrices of three dimensions
        and above.

        :raises ValueError: if a non-square matrix is given.
        :rtype: ``float``"""

        if not self.is_square():
            raise ValueError("{} is not square".format(self))
        if self.width() == 2:
            return ((self._rows[0][0] * self._rows[1][1])
             - (self._rows[0][1] * self._rows[1][0]))
        else:
            return sum([cell * self.cofactor(0, index) for index, cell
             in enumerate(self._rows[0])])


    def adjoint(self):
        """Returns the adjoint matrix of this matrix.

        :raises ValueError: if a non-square matrix is given.
        :rtype: ``Matrix``"""

        return self.cofactors().transposed()


    def inverse(self):
        """Returns the inverse matrix of this matrix.

        :raises ValueError: if the matrix is not invertible.
        :rtype: ``Matrix``"""

        det = self.determinant()
        if not det:
            raise ValueError("{} has no inverse: determinant is 0".format(self))
        return self.adjoint() * (1 / self.determinant())


    def column_space(self):
        """Returns the column space of matrix - the set of vectors reachable
        by its column vectors.

        :rtype: ``VectorSpan``"""

        return VectorSpan(*[Vector(col) for col in self.columns()])


    def rank(self):
        """The dimensions of the matrix's column space.

        :rtype: ``int``"""

        return self.column_space().rank()


    def is_full_rank(self):
        """Checks if the matrix is full rank - that is, whether its rank equals
        the number of dimensions of its column space.

        :rtype: ``bool``"""

        return self.rank() == len(self._rows)


    def gauss(self):
        """Performs Gaussian elimination on the matrix, changing it in place,
        and putting it into row echelon form (not *reduced* row echelon form).

        This is useful in solving systems of linear equations."""

        r, c = 0, 0
        while r < len(self._rows) and c < len(self._rows[0]):
            mx = max([[i, abs(self._rows[i][c])]
             for i in range(r, len(self._rows))], key=lambda x: x[1])[0]
            if self._rows[mx][c] == 0:
                c += 1
            else:
                self._rows[r], self._rows[mx] = self._rows[mx], self._rows[r]
            for i in range(r + 1, len(self._rows)):
                f = Fraction(self._rows[i][c]) / Fraction(self._rows[r][c])
                self._rows[i][c] = 0
                for j in range(c + 1, len(self._rows[0])):
                    self._rows[i][j] -= self._rows[c][j] * f
            r, c = r + 1, c + 1
        self._rows = [[float(val) for val in row] for row in self._rows]


    def is_row_echelon(self):
        """Checks to see if the matrix is in row echelon form.

        :rtype: ``bool``"""

        in_zero, lead = False, -1
        for row in self._rows:
            if set(row) == {0}:
                in_zero = True
            else:
                lead_coefficient_pos = row.index(list(filter(bool, row))[0])
                if lead_coefficient_pos <= lead: return False
                lead = lead_coefficient_pos
            if in_zero and not set(row) == {0}: return False
        return True


    def is_reduced_row_echelon(self):
        """Checks to see if the matrix is in reduced row echelon form.

        :rtype: ``bool``"""

        if not self.is_row_echelon(): return False
        for row in self._rows:
            if set(row) != {0}:
                for i, val in enumerate(row):
                    if val != 0:
                        if val != 1: return False
                        column = [row[i] for row in self._rows]
                        if set(column) != {1, 0}: return False
                        if column.count(1) != 1: return False
                        break
        return True
