# This file is a part of physics
#
# Copyright (c) 2018 The physics Authors (see AUTHORS)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
physics.errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It contains the Errors class.

It could be used to do arithmetic operations using
numbers and their errors on themselves.
"""


class Errors:

    """
    The Errors class is used to define
    a number with an absolute, relative or
    percentage error and do arithmetic
    operations with them.
    """

    def __init__(self, number, **settings):
        r"""
        It initializes the object, checks
        if an absolute, relative or percentage is
        given and if not it generates an absolute
        error following the established rules during
        physics conventions.

        :param number: The number you've chosen
        :type number: float or integer
        :param \**settings: A dictionary of errors. It must include an absolute, relative or percentual error at all.
        :type \**settings: dict
        """
        self.number = number
        if 'absolute_error' in settings:
            self.absolute_error = settings['absolute_error']
            self.relative_error = settings['absolute_error'] / number
            self.percentage_error = round(
                settings['absolute_error'] / number,
                4) * 100

        elif 'relative_error' in Errors:
            self.absolute_error = settings['relative_error'] * number
            self.relative_error = settings['relative_error']
            self.percentage_error = settings['relative_error'] * 100

        elif 'percentage_error' in Errors:
            self.absolute_error = (settings['percentage_error'] / 100) * number
            self.relative_error = settings['percentage_error'] / 100
            self.percentage_error = settings['percentage_error']

        else:

            if int(number) is 0:
                index = 0
                list_number = list(str(number - int(number))[2:])
                for _ in list_number:
                    list_number[index] = '0'
                    index += 1
                list_number[-1] = '1'
                del index
                self.absolute_error = float('0.' + (''.join(list_number)))
            else:
                self.absolute_error = 1
            self.relative_error = self.absolute_error / number
            self.percentage_error = round(self.relative_error, 4) * 100

    def __radd__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse Addition, summing
        absolute errors and numbers.

        :param second_number: The number you want to add.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __iadd__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline Addition, summing
        absolute errors and numbers.

        :param second_number: The number you want to add.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __add__(self, second_number):
        """
        That function is used to
        establish the result of
        an Addition, summing
        absolute errors and numbers.

        :param second_number: The number you want to add.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number + second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number + second_number,
                          absolute_error=self.absolute_error)

    def __sub__(self, second_number):
        """
        That function is used to
        establish the result of
        a Subtraction, summing
        absolute Errors and
        subtracting numbers.

        :param second_number: The number you want to substrate.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __rsub__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse Subtraction,
        summing absolute Errors
        and subtracting numbers.

        :param second_number: The number you want to substrate.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __isub__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline Subtraction,
        summing absolute Errors
        and subtracting numbers.

        :param second_number: The number you want to substrate.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number - second_number.number,
                          absolute_error=(self.absolute_error +
                                          second_number.absolute_error))
        else:
            return Errors(self.number - second_number,
                          absolute_error=self.absolute_error)

    def __mul__(self, second_number):
        """
        That function is used to
        establish the result of
        a Multiplication,
        summing relative errors
        and multiplying numbers.

        :param second_number: The number you want to multiply.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __rmul__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse Multiplication,
        summing relative errors
        and multiplying numbers.

        :param second_number: The number you want to multiply.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __imul__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline Multiplication,
        summing relative errors
        and multiplying numbers.

        :param second_number: The number you want to multiply.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number * second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number * second_number,
                          relative_error=self.relative_error)

    def __truediv__(self, second_number):
        """
        That function is used to
        establish the result of
        a True Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __rtruediv__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse True Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __itruediv__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline True Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number / second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number / second_number,
                          relative_error=self.relative_error)

    def __floordiv__(self, second_number):
        """
        That function is used to
        establish the result of
        a Floor Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __rfloordiv__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse Floor Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __ifloordiv__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline Floor Division,
        summing relative errors
        and dividing numbers.

        :param second_number: The number you want to divide.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number // second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number // second_number,
                          relative_error=self.relative_error)

    def __mod__(self, second_number):
        """
        That function is used to
        establish the result of
        a Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.

        :param second_number: The number you want to get the modulo.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __rmod__(self, second_number):
        """
        That function is used to
        establish the result of
        a Reverse Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.

        :param second_number: The number you want to get the modulo.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __imod__(self, second_number):
        """
        That function is used to
        establish the result of
        an Inline Modulo,
        summing relative errors
        and giving the remainder of
        the divided numbers.

        :param second_number: The number you want to get the modulo.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            return Errors(self.number % second_number.number,
                          relative_error=(self.relative_error +
                                          second_number.relative_error))
        else:
            return Errors(self.number % second_number,
                          relative_error=self.relative_error)

    def __pow__(self, second_number, modulo=0):
        """
        That function is used to
        establish the result of
        an Exponentiation,
        multiplying the first
        relative error for the second
        number and giving arithmetic power.

        :param second_number: The number you want to get the power.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if modulo is 0:
                return Errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return Errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return Errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return Errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __rpow__(self, second_number, modulo=0):
        """
        That function is used to
        establish the result of
        a Reverse Exponentiation,
        multiplying the first
        relative error for the second
        number and giving arithmetic power.

        :param second_number: The number you want to get the power.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if modulo is 0:
                return Errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return Errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return Errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return Errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __ipow__(self, second_number, modulo=0):
        """
        That function is used to
        establish the result of
        an Inline Exponentiation,
        multiplying the first
        relative error for the second
        number and giving arithmetic power.

        :param second_number: The number you want to get the power.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if modulo is 0:
                return Errors(self.number ** second_number.number,
                              relative_error=(self.relative_error *
                                              second_number.number))
            else:
                return Errors((self.number ** second_number.number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number.number))
        else:
            if modulo is 0:
                return Errors(self.number ** second_number,
                              relative_error=(self.relative_error *
                                              second_number))
            else:
                return Errors((self.number ** second_number) %
                              modulo, relative_error=(self.relative_error *
                                                      second_number))

    def __abs__(self):
        """
        That function is used to
        return the absolute value
        of the chosen number.
        """
        return abs(self.number)

    def __neg__(self):
        """
        That function is used to
        return the negative value
        of the chosen number.
        """
        return -(abs(self.number))

    def __pos__(self):
        """
        That function is used to
        return the positive value
        of the chosen number.
        """
        return abs(self.number)

    def __invert__(self):
        """
        That function is used to
        return the inverted value
        of the chosen number.
        """
        return ~self.number

    def __len__(self) -> int:
        """
        That function is used to
        return the number of
        digits of the
        chosen number.
        """
        return len(str(self.number))

    def __lt__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "<".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if self.percentage_error < second_number.percentage_error:
                return True
            else:
                return False
        else:
            return self < Errors(second_number)

    def __le__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "<=".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if self.percentage_error <= second_number.percentage_error:
                return True
            else:
                return False
        else:
            return self <= Errors(second_number)

    def __eq__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "==".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if (self.relative_error ==
                second_number.relative_error) and (self.number ==
                                                   second_number.number):
                return True
            else:
                return False
        else:
            return self == Errors(second_number)

    def __ne__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "!=".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if (self.relative_error !=
                second_number.relative_error) and (self.number !=
                                                   second_number.number):
                return True
            else:
                return False
        else:
            return self != Errors(second_number)

    def __gt__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using ">".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if self.percentage_error > second_number.percentage_error:
                return True
            else:
                return False
        else:
            return self > Errors(second_number)

    def __ge__(self, second_number) -> bool:
        """
        That function is used to
        compare two numbers
        using ">=".

        :param second_number: The number you want to compare.
        :type second_number: integer, float or Errors
        """
        if isinstance(second_number, Errors):
            if self.percentage_error >= second_number.percentage_error:
                return True
            else:
                return False
        else:
            return self >= Errors(second_number)

    def __int__(self) -> int:
        """
        That function is used to
        return the integer
        of the chosen number.
        """
        return self.number

    def __str__(self) -> str:
        """
        That function is used to
        return a string representation
        of the chosen number.
        """
        return str(self.number) + " ± " + str(self.absolute_error)

    def __float__(self) -> float:
        """
        That function is used to
        return the float
        of the chosen number.
        """
        return float(self.number)

    def __round__(self, digits=0) -> float:
        """
        That function is used to
        round the chosen number.
        """
        return round(self.number, digits)
