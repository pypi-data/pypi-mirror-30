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
physics.proportionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It contains the Proportionality class.

It could be used to define a proportionality relation
between numbers.
"""


class Proportionality:

    """
    The proportionality class is used to
    calculate and use proportionality using
    numbers.
    percentage error and do arithmetic
    """

    def __init__(self, **options):
        r"""
        It initializes the object and
        it checks **options parameter,
        and then get the constant of the
        proportionality.

        :param \**options: The constant and relation or a dict of numbers (x is the key, y the value)
        :type \**options: dict
        :raises MissingNeededParameters: It throws an exception if some parameters are missing.
        :raises NoRelationError: It throws an exception if there are no relations between numbers.
        :raises LessThanTwoNumbersError: It throws an exception if there are less numbers than 2.
        """

        relations = ('direct_proportionality', 'inverse_proportionality',
                     'quadratic_relationship', 'inverse_proportionality')

        if 'constant' in options and 'relation' in options:
            self.constant = options['constant']
            relation = str(options['relation'].lower()).replace(" ", "_")
            if relation in relations:
                self.relation = options['relation'][
                                    0].upper() + options['relation'][1:].lower()
                if relation == 'direct_proportionality':
                    self.direct_proportionality = True
                    self.formula = 'k*x'
                elif relation == 'inverse_proportionality':
                    self.inverse_proportionality = True
                    self.formula = 'k/x'
                elif relation == 'quadratic_relationship':
                    self.quadratic_relationship = True
                    self.formula = 'k*(x**2)'
                elif relation == 'inverse_quadratic_relationship':
                    self.inverse_quadratic_relationship = True
                    self.formula = 'k/(x**2)'
                return
        elif 'numbers' in options:
            self.direct_proportionality = False
            self.inverse_proportionality = False
            self.quadratic_relationship = False
            self.inverse_quadratic_relationship = False
            constant = 0
            if 0 in options['numbers']:
                numbers_options = len(options['numbers']) - 1
            else:
                numbers_options = len(options['numbers'])
            if numbers_options > 1:
                last_constant = 0
                for x, y in options['numbers'].items():
                    if x is 0 or y is 0:
                        continue
                    constant = y / x
                    if last_constant == constant:
                        self.direct_proportionality = True
                        last_constant = constant
                    elif last_constant == 0:
                        self.direct_proportionality = True
                        last_constant = constant
                    else:
                        self.direct_proportionality = False
                        break
                if self.direct_proportionality:
                    self.constant = constant
                    self.relation = 'Direct proportionality'
                    self.formula = 'k*x'
                    return
                last_constant = 0
                constant = 0
                for x, y in options['numbers'].items():
                    if x is 0 or y is 0:
                        continue
                    constant = x * y
                    if last_constant == constant:
                        self.inverse_proportionality = True
                        last_constant = constant
                    elif last_constant == 0:
                        self.inverse_proportionality = True
                        last_constant = constant
                    else:
                        self.inverse_proportionality = False
                        break
                if self.inverse_proportionality:
                    self.constant = constant
                    self.relation = 'Inverse proportionality'
                    self.formula = 'k/x'
                    return
                last_constant = 0
                constant = 0
                for x, y in options['numbers'].items():
                    if x is 0 or y is 0:
                        continue
                    constant = y / (x ** 2)
                    if last_constant == constant:
                        self.quadratic_relationship = True
                        last_constant = constant
                    elif last_constant == 0:
                        self.quadratic_relationship = True
                        last_constant = constant
                    else:
                        self.quadratic_relationship = False
                        break
                if self.quadratic_relationship:
                    self.constant = constant
                    self.relation = 'Quadratic relationship'
                    self.formula = 'k*(x**2)'
                    return
                last_constant = 0
                constant = 0
                for x, y in options['numbers'].items():
                    if x is 0 or y is 0:
                        continue
                    constant = y * (x ** 2)
                    if last_constant == constant:
                        self.inverse_quadratic_relationship = True
                        last_constant = constant
                    elif last_constant == 0:
                        self.inverse_quadratic_relationship = True
                        last_constant = constant
                    else:
                        self.inverse_quadratic_relationship = False
                        break
                if self.inverse_quadratic_relationship:
                    self.constant = constant
                    self.relation = 'Inverse quadratic relationship'
                    self.formula = 'k/(x**2)'
                    return
                raise NoRelationError()
            else:
                raise LessThanTwoNumbersError()
        else:
            raise MissingNeededParameters()

    def calculate(self, **numbers):
        r"""
        Calculate the y using
        the formula created
        during proportionality
        check.

        :param \**numbers: The number you want to calculate.
        :type \**numbers: dict
        """
        if 'x' in numbers:
            k = self.constant
            x = numbers['x']
            return eval(self.formula)
        else:
            return

    def __str__(self) -> str:
        """
        Return the relation
        and the constant.

        :returns: The relation and its constant.
        :rtype: str
        """
        return ("Relation: " + self.relation +
                "\nConstant: " + self.constant)


class LessThanTwoNumbersError(Exception):
    """
    This exception is called when
    number of parameters are less
    than 2. 0 is not counted.
    """

    def __init__(self):
        Exception.__init__(self, "Numbers parameters are less than 2")


class NoRelationError(Exception):
    """
    This exception is called when
    there's no relation.
    """

    def __init__(self):
        Exception.__init__(self, "There's no relation")


class MissingNeededParameters(Exception):
    """
    This exception is called when
    constant and proportionality aren't
    in the parameters and numbers is missing.
    """

    def __init__(self):
        Exception.__init__(self, "There's no relation")
