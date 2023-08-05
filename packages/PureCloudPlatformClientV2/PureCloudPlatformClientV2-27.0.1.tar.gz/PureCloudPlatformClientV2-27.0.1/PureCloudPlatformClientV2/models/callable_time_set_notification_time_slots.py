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


class CallableTimeSetNotificationTimeSlots(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        CallableTimeSetNotificationTimeSlots - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'start_time': 'str',
            'stop_time': 'str',
            'day': 'int',
            'additional_properties': 'object'
        }

        self.attribute_map = {
            'start_time': 'startTime',
            'stop_time': 'stopTime',
            'day': 'day',
            'additional_properties': 'additionalProperties'
        }

        self._start_time = None
        self._stop_time = None
        self._day = None
        self._additional_properties = None

    @property
    def start_time(self):
        """
        Gets the start_time of this CallableTimeSetNotificationTimeSlots.


        :return: The start_time of this CallableTimeSetNotificationTimeSlots.
        :rtype: str
        """
        return self._start_time

    @start_time.setter
    def start_time(self, start_time):
        """
        Sets the start_time of this CallableTimeSetNotificationTimeSlots.


        :param start_time: The start_time of this CallableTimeSetNotificationTimeSlots.
        :type: str
        """
        
        self._start_time = start_time

    @property
    def stop_time(self):
        """
        Gets the stop_time of this CallableTimeSetNotificationTimeSlots.


        :return: The stop_time of this CallableTimeSetNotificationTimeSlots.
        :rtype: str
        """
        return self._stop_time

    @stop_time.setter
    def stop_time(self, stop_time):
        """
        Sets the stop_time of this CallableTimeSetNotificationTimeSlots.


        :param stop_time: The stop_time of this CallableTimeSetNotificationTimeSlots.
        :type: str
        """
        
        self._stop_time = stop_time

    @property
    def day(self):
        """
        Gets the day of this CallableTimeSetNotificationTimeSlots.


        :return: The day of this CallableTimeSetNotificationTimeSlots.
        :rtype: int
        """
        return self._day

    @day.setter
    def day(self, day):
        """
        Sets the day of this CallableTimeSetNotificationTimeSlots.


        :param day: The day of this CallableTimeSetNotificationTimeSlots.
        :type: int
        """
        
        self._day = day

    @property
    def additional_properties(self):
        """
        Gets the additional_properties of this CallableTimeSetNotificationTimeSlots.


        :return: The additional_properties of this CallableTimeSetNotificationTimeSlots.
        :rtype: object
        """
        return self._additional_properties

    @additional_properties.setter
    def additional_properties(self, additional_properties):
        """
        Sets the additional_properties of this CallableTimeSetNotificationTimeSlots.


        :param additional_properties: The additional_properties of this CallableTimeSetNotificationTimeSlots.
        :type: object
        """
        
        self._additional_properties = additional_properties

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

