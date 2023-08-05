# coding: utf-8

"""
Copyright 2016 SmartBear Software

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

    Ref: https://github.com/swagger-api/swagger-codegen
"""

from pprint import pformat
from six import iteritems
import re


class PromptNotificationNotification(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        PromptNotificationNotification - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'name': 'str',
            'description': 'str',
            'current_operation': 'PromptNotificationNotificationCurrentOperation'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'description': 'description',
            'current_operation': 'currentOperation'
        }

        self._id = None
        self._name = None
        self._description = None
        self._current_operation = None

    @property
    def id(self):
        """
        Gets the id of this PromptNotificationNotification.


        :return: The id of this PromptNotificationNotification.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this PromptNotificationNotification.


        :param id: The id of this PromptNotificationNotification.
        :type: str
        """
        
        self._id = id

    @property
    def name(self):
        """
        Gets the name of this PromptNotificationNotification.


        :return: The name of this PromptNotificationNotification.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this PromptNotificationNotification.


        :param name: The name of this PromptNotificationNotification.
        :type: str
        """
        
        self._name = name

    @property
    def description(self):
        """
        Gets the description of this PromptNotificationNotification.


        :return: The description of this PromptNotificationNotification.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Sets the description of this PromptNotificationNotification.


        :param description: The description of this PromptNotificationNotification.
        :type: str
        """
        
        self._description = description

    @property
    def current_operation(self):
        """
        Gets the current_operation of this PromptNotificationNotification.


        :return: The current_operation of this PromptNotificationNotification.
        :rtype: PromptNotificationNotificationCurrentOperation
        """
        return self._current_operation

    @current_operation.setter
    def current_operation(self, current_operation):
        """
        Sets the current_operation of this PromptNotificationNotification.


        :param current_operation: The current_operation of this PromptNotificationNotification.
        :type: PromptNotificationNotificationCurrentOperation
        """
        
        self._current_operation = current_operation

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

