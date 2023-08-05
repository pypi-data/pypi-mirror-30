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


class OrphanRecording(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        OrphanRecording - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'name': 'str',
            'created_time': 'datetime',
            'recovered_time': 'datetime',
            'provider_type': 'str',
            'media_size_bytes': 'int',
            'media_type': 'str',
            'file_state': 'str',
            'provider_endpoint': 'Endpoint',
            'recording': 'Recording',
            'orphan_status': 'str',
            'self_uri': 'str'
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'created_time': 'createdTime',
            'recovered_time': 'recoveredTime',
            'provider_type': 'providerType',
            'media_size_bytes': 'mediaSizeBytes',
            'media_type': 'mediaType',
            'file_state': 'fileState',
            'provider_endpoint': 'providerEndpoint',
            'recording': 'recording',
            'orphan_status': 'orphanStatus',
            'self_uri': 'selfUri'
        }

        self._id = None
        self._name = None
        self._created_time = None
        self._recovered_time = None
        self._provider_type = None
        self._media_size_bytes = None
        self._media_type = None
        self._file_state = None
        self._provider_endpoint = None
        self._recording = None
        self._orphan_status = None
        self._self_uri = None

    @property
    def id(self):
        """
        Gets the id of this OrphanRecording.
        The globally unique identifier for the object.

        :return: The id of this OrphanRecording.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this OrphanRecording.
        The globally unique identifier for the object.

        :param id: The id of this OrphanRecording.
        :type: str
        """
        
        self._id = id

    @property
    def name(self):
        """
        Gets the name of this OrphanRecording.


        :return: The name of this OrphanRecording.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Sets the name of this OrphanRecording.


        :param name: The name of this OrphanRecording.
        :type: str
        """
        
        self._name = name

    @property
    def created_time(self):
        """
        Gets the created_time of this OrphanRecording.
        Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :return: The created_time of this OrphanRecording.
        :rtype: datetime
        """
        return self._created_time

    @created_time.setter
    def created_time(self, created_time):
        """
        Sets the created_time of this OrphanRecording.
        Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :param created_time: The created_time of this OrphanRecording.
        :type: datetime
        """
        
        self._created_time = created_time

    @property
    def recovered_time(self):
        """
        Gets the recovered_time of this OrphanRecording.
        Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :return: The recovered_time of this OrphanRecording.
        :rtype: datetime
        """
        return self._recovered_time

    @recovered_time.setter
    def recovered_time(self, recovered_time):
        """
        Sets the recovered_time of this OrphanRecording.
        Date time is represented as an ISO-8601 string. For example: yyyy-MM-ddTHH:mm:ss.SSSZ

        :param recovered_time: The recovered_time of this OrphanRecording.
        :type: datetime
        """
        
        self._recovered_time = recovered_time

    @property
    def provider_type(self):
        """
        Gets the provider_type of this OrphanRecording.


        :return: The provider_type of this OrphanRecording.
        :rtype: str
        """
        return self._provider_type

    @provider_type.setter
    def provider_type(self, provider_type):
        """
        Sets the provider_type of this OrphanRecording.


        :param provider_type: The provider_type of this OrphanRecording.
        :type: str
        """
        allowed_values = ["EDGE", "CHAT", "EMAIL", "SCREEN_RECORDING"]
        if provider_type.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for provider_type -> " + provider_type
            self._provider_type = "outdated_sdk_version"
        else:
            self._provider_type = provider_type

    @property
    def media_size_bytes(self):
        """
        Gets the media_size_bytes of this OrphanRecording.


        :return: The media_size_bytes of this OrphanRecording.
        :rtype: int
        """
        return self._media_size_bytes

    @media_size_bytes.setter
    def media_size_bytes(self, media_size_bytes):
        """
        Sets the media_size_bytes of this OrphanRecording.


        :param media_size_bytes: The media_size_bytes of this OrphanRecording.
        :type: int
        """
        
        self._media_size_bytes = media_size_bytes

    @property
    def media_type(self):
        """
        Gets the media_type of this OrphanRecording.


        :return: The media_type of this OrphanRecording.
        :rtype: str
        """
        return self._media_type

    @media_type.setter
    def media_type(self, media_type):
        """
        Sets the media_type of this OrphanRecording.


        :param media_type: The media_type of this OrphanRecording.
        :type: str
        """
        allowed_values = ["CALL", "CHAT", "EMAIL", "SCREEN"]
        if media_type.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for media_type -> " + media_type
            self._media_type = "outdated_sdk_version"
        else:
            self._media_type = media_type

    @property
    def file_state(self):
        """
        Gets the file_state of this OrphanRecording.


        :return: The file_state of this OrphanRecording.
        :rtype: str
        """
        return self._file_state

    @file_state.setter
    def file_state(self, file_state):
        """
        Sets the file_state of this OrphanRecording.


        :param file_state: The file_state of this OrphanRecording.
        :type: str
        """
        allowed_values = ["ARCHIVED", "AVAILABLE", "DELETED", "RESTORED", "RESTORING", "UPLOADING"]
        if file_state.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for file_state -> " + file_state
            self._file_state = "outdated_sdk_version"
        else:
            self._file_state = file_state

    @property
    def provider_endpoint(self):
        """
        Gets the provider_endpoint of this OrphanRecording.


        :return: The provider_endpoint of this OrphanRecording.
        :rtype: Endpoint
        """
        return self._provider_endpoint

    @provider_endpoint.setter
    def provider_endpoint(self, provider_endpoint):
        """
        Sets the provider_endpoint of this OrphanRecording.


        :param provider_endpoint: The provider_endpoint of this OrphanRecording.
        :type: Endpoint
        """
        
        self._provider_endpoint = provider_endpoint

    @property
    def recording(self):
        """
        Gets the recording of this OrphanRecording.


        :return: The recording of this OrphanRecording.
        :rtype: Recording
        """
        return self._recording

    @recording.setter
    def recording(self, recording):
        """
        Sets the recording of this OrphanRecording.


        :param recording: The recording of this OrphanRecording.
        :type: Recording
        """
        
        self._recording = recording

    @property
    def orphan_status(self):
        """
        Gets the orphan_status of this OrphanRecording.
        The status of the orphaned recording's conversation.

        :return: The orphan_status of this OrphanRecording.
        :rtype: str
        """
        return self._orphan_status

    @orphan_status.setter
    def orphan_status(self, orphan_status):
        """
        Sets the orphan_status of this OrphanRecording.
        The status of the orphaned recording's conversation.

        :param orphan_status: The orphan_status of this OrphanRecording.
        :type: str
        """
        allowed_values = ["NO_CONVERSATION", "UNKNOWN_CONVERSATION", "CONVERSATION_NOT_COMPLETE", "CONVERSATION_NOT_EVALUATED", "EVALUATED"]
        if orphan_status.lower() not in map(str.lower, allowed_values):
            # print "Invalid value for orphan_status -> " + orphan_status
            self._orphan_status = "outdated_sdk_version"
        else:
            self._orphan_status = orphan_status

    @property
    def self_uri(self):
        """
        Gets the self_uri of this OrphanRecording.
        The URI for this object

        :return: The self_uri of this OrphanRecording.
        :rtype: str
        """
        return self._self_uri

    @self_uri.setter
    def self_uri(self, self_uri):
        """
        Sets the self_uri of this OrphanRecording.
        The URI for this object

        :param self_uri: The self_uri of this OrphanRecording.
        :type: str
        """
        
        self._self_uri = self_uri

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

