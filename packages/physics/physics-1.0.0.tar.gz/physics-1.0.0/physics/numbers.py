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
physics.numbers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It contains the Numbers class.

It could be used to define numbers using significant
digits.
"""


class Numbers:

    """
    The Numbers class is used to define
    a number using its significant digits.
    """

    def __init__(self, number):
        """
        It initializes the object and
        get the significant digits
        following the established rules
        during physics conventions.

        :param number: The number you've chosen.
        :type number: int or float
        """
        significant_digits = 0
        after_comma = 0
        new_number = ''
        comma_encountered = False
        zero_encountered = False
        for digit in str(number):
            if digit is '.':
                new_number += '.'
                comma_encountered = True
                continue
            if zero_encountered:
                significant_digits += 1
                new_number += digit
                if comma_encountered:
                    after_comma += 1
            elif digit != '0' and not zero_encountered:
                zero_encountered = True
                significant_digits += 1
                new_number += digit
                if comma_encountered:
                    after_comma += 1

        self.significant_digits = significant_digits
        self.number = float(new_number)
        self.after_comma = after_comma

    def __add__(self, other_number):
        """
        That function is used to
        establish the result of
        an Addition, using significant
        digits.

        :param other_number: The number you want to add.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number + other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number + other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number + x.number), self.after_comma))
            else:
                return Numbers(round((self.number + x.number), x.after_comma))

    def __iadd__(self, other_number):
        """
        That function is used to
        establish the result of
        an Inline Addition, using significant
        digits.

        :param other_number: The number you want to add.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number + other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number + other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number + x.number), self.after_comma))
            else:
                return Numbers(round((self.number + x.number), x.after_comma))

    def __radd__(self, other_number):
        """
        That function is used to
        establish the result of
        a Reverse Addition, using significant
        digits.

        :param other_number: The number you want to add.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number + other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number + other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number + x.number), self.after_comma))
            else:
                return Numbers(round((self.number + x.number), x.after_comma))

    def __sub__(self, other_number):
        """
        That function is used to
        establish the result of
        a Subtraction, using significant
        digits.

        :param other_number: The number you want to subtract.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number - other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number - other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number - x.number), self.after_comma))
            else:
                return Numbers(round((self.number - x.number), x.after_comma))

    def __isub__(self, other_number):
        """
        That function is used to
        establish the result of
        an Inline Subtraction, using significant
        digits.

        :param other_number: The number you want to subtract.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number - other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number - other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number - x.number), self.after_comma))
            else:
                return Numbers(round((self.number - x.number), x.after_comma))

    def __rsub__(self, other_number):
        """
        That function is used to
        establish the result of
        a Reverse Subtraction, using significant
        digits.

        :param other_number: The number you want to subtract.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.after_comma > self.after_comma:
                return Numbers(round((self.number - other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number - other_number.number), other_number.after_comma))

        else:
            x = Numbers(int(other_number))
            if x.after_comma > self.after_comma:
                return Numbers(round((self.number - x.number), self.after_comma))
            else:
                return Numbers(round((self.number - x.number), x.after_comma))

    def __floordiv__(self, other_number):
        """
        That function is used to
        establish the result of
        a Floor Division, using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number // other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number // other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number // other_number), self.significant_digits))

    def __ifloordiv__(self, other_number):
        """
        That function is used to
        establish the result of
        an Inline Floor
        Division, using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number // other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number // other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number // other_number), self.significant_digits))

    def __rfloordiv__(self, other_number):
        """
        That function is used to
        establish the result of
        a Reverse Floor Division,
        using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number // other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number // other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number // other_number), self.significant_digits))

    def __truediv__(self, other_number):
        """
        That function is used to
        establish the result of
        a True Division,
        using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number / other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number / other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number / other_number), self.significant_digits))

    def __itruediv__(self, other_number):
        """
        That function is used to
        establish the result of
        an Inline True
        Division, using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number / other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number / other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number / other_number), self.significant_digits))

    def __rtruediv__(self, other_number):
        """
        That function is used to
        establish the result of
        a Reverse True Division,
        using significant
        digits.

        :param other_number: The number you want to divide.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number / other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number / other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number / other_number), self.significant_digits))

    def __mul__(self, other_number):
        """
        That function is used to
        establish the result of
        a Multiplication,
        using significant
        digits.

        :param other_number: The number you want to multiply.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number * other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number * other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number * other_number), self.significant_digits))

    def __imul__(self, other_number):
        """
        That function is used to
        establish the result of
        an Inline Multiplication,
        using significant
        digits.

        :param other_number: The number you want to multiply.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number * other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number * other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number * other_number), self.significant_digits))

    def __rmul__(self, other_number):
        """
        That function is used to
        establish the result of
        a Reverse Multiplication,
        using significant
        digits.

        :param other_number: The number you want to multiply.
        :type other_number: integer, float or Numbers
        :returns: The result
        :rtype: Integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if other_number.significant_digits > self.significant_digits:
                return Numbers(round((self.number * other_number.number), self.after_comma))
            else:
                return Numbers(round((self.number * other_number.number), other_number.after_comma))

        else:
            return Numbers(round((self.number * other_number), self.significant_digits))

    def __abs__(self):
        """
        That function is used to
        obtain the absolute value
        of the number.

        :returns: The Absolute Value.
        :rtype: int or float
        """
        return abs(self.number)

    def __neg__(self):
        """
        That function is used to
        return the negative value
        of the chosen number.

        :returns: The Negative Value.
        :rtype: int or float
        """
        return -(abs(self.number))

    def __pos__(self):
        """
        That function is used to
        return the positive value
        of the chosen number.

        :returns: The Positive Value.
        :rtype: int or float
        """
        return abs(self.number)

    def __invert__(self):
        """
        That function is used to
        return the inverted value
        of the chosen number.

        :returns: The Inverted Value.
        :rtype: int or float
        """
        if self.number < 0:
            return abs(self.number)
        else:
            return -abs(self.number)

    def __len__(self) -> int:
        """
        That function is used to
        return the number of
        digits of the
        chosen number.

        :returns: The length.
        :rtype: Integer
        """
        return len(str(self.number))

    def __int__(self) -> int:
        """
        That function is used to
        return the integer
        of the chosen number.

        :returns: The integer of the number.
        :rtype: int
        """
        return int(self.number)

    def __str__(self) -> str:
        """
        That function is used to
        return a string rappresentation
        of the chosen number.

        :returns: The String.
        :rtype: str
        """
        return str(self.number)

    def __float__(self) -> float:
        """
        That function is used to
        return the float
        of the chosen number.

        :returns: The Float.
        :rtype: float
        """
        return float(self.number)

    def __round__(self, digits=0) -> float:
        """
        That function is used to
        round the chosen number.

        :returns: The Rounded Value.
        :rtype: float
        """
        return round(self.number, digits)

    def __lt__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "<".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if self.number < other_number.number:
                return True
            else:
                return False
        else:
            return self < Numbers(other_number)

    def __le__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "<=".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if self.number <= other_number.number:
                return True
            else:
                return False
        else:
            return self <= Numbers(other_number)

    def __eq__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "==".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if (self.significant_digits ==
                other_number.significant_digits) and (self.number ==
                                                      other_number.number):
                return True
            else:
                return False
        else:
            return self == Numbers(other_number)

    def __ne__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using "!=".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if (self.significant_digits !=
                other_number.significant_digits) and (self.number !=
                                                      other_number.number):
                return True
            else:
                return False
        else:
            return self != Numbers(other_number)

    def __gt__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using ">".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if self.number > other_number.number:
                return True
            else:
                return False
        else:
            return self > Numbers(other_number)

    def __ge__(self, other_number) -> bool:
        """
        That function is used to
        compare two numbers
        using ">=".

        :param other_number: The number you want to compare.
        :type other_number: integer, float or Numbers
        """
        if isinstance(other_number, Numbers):
            if self.number >= other_number.number:
                return True
            else:
                return False
        else:
            return self >= Numbers(other_number)
