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
physics.gravity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
It contains the Gravity class.

It could be used to get the gravity force of
some objects.
"""


class Gravity:

    """
    Given two masses and their
    distance, it calculates the
    Gravity force between them
    """

    def __init__(self, **options):
        r"""
        It calculates the gravity force
        by using the parameters given into
        options

        :param \**options: The mass, the second_mass and the distance of the objects or just a mass with the earth flag.
        :type \**options: dict
        :raises MissingNeededParameters: It throws an exception when some parameters are missing.
        """
        if 'earth' in options and 'mass' in options and options['earth']:
            universal_gravity_constant = float('6.67e-11')
            earth_mass = float('5.972e24')
            self.distance = 6400
            self.mass = options['mass']
            self.gravity_force = universal_gravity_constant * \
                earth_mass * self.mass / (self.distance**2)
            return
        if 'mass' in options and 'second_mass' in options and 'distance' in options:
            universal_gravity_constant = 6.67e-11
            self.mass = options['mass']
            self.second_mass = options['second_mass']
            self.distance = options['distance']
            self.gravity_force = universal_gravity_constant * \
                (self.second_mass * self.mass / (self.distance**2))
            return
        raise MissingNeededParameters()


class MissingNeededParameters(Exception):

    """
    This exception is called when
    there are some missing parameters
    """

    def __init__(self):
        Exception.__init__(
            self,
            "There are some missing parameters, it is impossible to calculate the Gravity force")
