# coding: utf-8

"""

    No descripton provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)

    
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

from pprint import pformat
from six import iteritems
import re


class HyperParametersExperiments(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, name=None, double_values=None, int_values=None, string_values=None, double_range=None, int_range=None):
        """
        HyperParametersExperiments - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'name': 'str',
            'double_values': 'list[float]',
            'int_values': 'list[int]',
            'string_values': 'list[str]',
            'double_range': 'HyperParametersExperimentsDoubleRange',
            'int_range': 'HyperParametersExperimentsIntRange'
        }

        self.attribute_map = {
            'name': 'name',
            'double_values': 'double_values',
            'int_values': 'int_values',
            'string_values': 'string_values',
            'double_range': 'double_range',
            'int_range': 'int_range'
        }

        self._name = name
        self._double_values = double_values
        self._int_values = int_values
        self._string_values = string_values
        self._double_range = double_range
        self._int_range = int_range

    @property
    def name(self):
        """
        Gets the name of this HyperParametersExperiments.
        Name of the parameter which we want to tune

        :return: The name of this HyperParametersExperiments.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this HyperParametersExperiments.
        Name of the parameter which we want to tune

        :param name: The name of this HyperParametersExperiments.
        :type: str
        """

        self._name = name

    @property
    def double_values(self):
        """
        Gets the double_values of this HyperParametersExperiments.


        :return: The double_values of this HyperParametersExperiments.
        :rtype: list[float]
        """
        return self._double_values

    @double_values.setter
    def double_values(self, double_values):
        """
        Sets the double_values of this HyperParametersExperiments.


        :param double_values: The double_values of this HyperParametersExperiments.
        :type: list[float]
        """

        self._double_values = double_values

    @property
    def int_values(self):
        """
        Gets the int_values of this HyperParametersExperiments.


        :return: The int_values of this HyperParametersExperiments.
        :rtype: list[int]
        """
        return self._int_values

    @int_values.setter
    def int_values(self, int_values):
        """
        Sets the int_values of this HyperParametersExperiments.


        :param int_values: The int_values of this HyperParametersExperiments.
        :type: list[int]
        """

        self._int_values = int_values

    @property
    def string_values(self):
        """
        Gets the string_values of this HyperParametersExperiments.


        :return: The string_values of this HyperParametersExperiments.
        :rtype: list[str]
        """
        return self._string_values

    @string_values.setter
    def string_values(self, string_values):
        """
        Sets the string_values of this HyperParametersExperiments.


        :param string_values: The string_values of this HyperParametersExperiments.
        :type: list[str]
        """

        self._string_values = string_values

    @property
    def double_range(self):
        """
        Gets the double_range of this HyperParametersExperiments.


        :return: The double_range of this HyperParametersExperiments.
        :rtype: HyperParametersExperimentsDoubleRange
        """
        return self._double_range

    @double_range.setter
    def double_range(self, double_range):
        """
        Sets the double_range of this HyperParametersExperiments.


        :param double_range: The double_range of this HyperParametersExperiments.
        :type: HyperParametersExperimentsDoubleRange
        """

        self._double_range = double_range

    @property
    def int_range(self):
        """
        Gets the int_range of this HyperParametersExperiments.


        :return: The int_range of this HyperParametersExperiments.
        :rtype: HyperParametersExperimentsIntRange
        """
        return self._int_range

    @int_range.setter
    def int_range(self, int_range):
        """
        Sets the int_range of this HyperParametersExperiments.


        :param int_range: The int_range of this HyperParametersExperiments.
        :type: HyperParametersExperimentsIntRange
        """

        self._int_range = int_range

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
