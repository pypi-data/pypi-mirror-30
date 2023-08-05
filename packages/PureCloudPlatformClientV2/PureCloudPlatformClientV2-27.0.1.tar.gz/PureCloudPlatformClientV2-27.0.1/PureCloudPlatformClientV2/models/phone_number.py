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


class PhoneNumber(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        PhoneNumber - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'display': 'str',
            'extension': 'int',
            'accepts_sms': 'bool',
            'user_input': 'str',
            'e164': 'str',
            'country_code': 'str'
        }

        self.attribute_map = {
            'display': 'display',
            'extension': 'extension',
            'accepts_sms': 'acceptsSMS',
            'user_input': 'userInput',
            'e164': 'e164',
            'country_code': 'countryCode'
        }

        self._display = None
        self._extension = None
        self._accepts_sms = None
        self._user_input = None
        self._e164 = None
        self._country_code = None

    @property
    def display(self):
        """
        Gets the display of this PhoneNumber.


        :return: The display of this PhoneNumber.
        :rtype: str
        """
        return self._display

    @display.setter
    def display(self, display):
        """
        Sets the display of this PhoneNumber.


        :param display: The display of this PhoneNumber.
        :type: str
        """
        
        self._display = display

    @property
    def extension(self):
        """
        Gets the extension of this PhoneNumber.


        :return: The extension of this PhoneNumber.
        :rtype: int
        """
        return self._extension

    @extension.setter
    def extension(self, extension):
        """
        Sets the extension of this PhoneNumber.


        :param extension: The extension of this PhoneNumber.
        :type: int
        """
        
        self._extension = extension

    @property
    def accepts_sms(self):
        """
        Gets the accepts_sms of this PhoneNumber.


        :return: The accepts_sms of this PhoneNumber.
        :rtype: bool
        """
        return self._accepts_sms

    @accepts_sms.setter
    def accepts_sms(self, accepts_sms):
        """
        Sets the accepts_sms of this PhoneNumber.


        :param accepts_sms: The accepts_sms of this PhoneNumber.
        :type: bool
        """
        
        self._accepts_sms = accepts_sms

    @property
    def user_input(self):
        """
        Gets the user_input of this PhoneNumber.


        :return: The user_input of this PhoneNumber.
        :rtype: str
        """
        return self._user_input

    @user_input.setter
    def user_input(self, user_input):
        """
        Sets the user_input of this PhoneNumber.


        :param user_input: The user_input of this PhoneNumber.
        :type: str
        """
        
        self._user_input = user_input

    @property
    def e164(self):
        """
        Gets the e164 of this PhoneNumber.


        :return: The e164 of this PhoneNumber.
        :rtype: str
        """
        return self._e164

    @e164.setter
    def e164(self, e164):
        """
        Sets the e164 of this PhoneNumber.


        :param e164: The e164 of this PhoneNumber.
        :type: str
        """
        
        self._e164 = e164

    @property
    def country_code(self):
        """
        Gets the country_code of this PhoneNumber.


        :return: The country_code of this PhoneNumber.
        :rtype: str
        """
        return self._country_code

    @country_code.setter
    def country_code(self, country_code):
        """
        Sets the country_code of this PhoneNumber.


        :param country_code: The country_code of this PhoneNumber.
        :type: str
        """
        
        self._country_code = country_code

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

