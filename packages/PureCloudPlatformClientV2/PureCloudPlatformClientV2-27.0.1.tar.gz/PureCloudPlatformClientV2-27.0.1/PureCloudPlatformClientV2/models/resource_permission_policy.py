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


class ResourcePermissionPolicy(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self):
        """
        ResourcePermissionPolicy - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'domain': 'str',
            'entity_name': 'str',
            'policy_name': 'str',
            'policy_description': 'str',
            'action_set_key': 'str',
            'allow_conditions': 'bool',
            'resource_condition_node': 'ResourceConditionNode',
            'named_resources': 'list[str]',
            'resource_condition': 'str',
            'action_set': 'list[str]'
        }

        self.attribute_map = {
            'id': 'id',
            'domain': 'domain',
            'entity_name': 'entityName',
            'policy_name': 'policyName',
            'policy_description': 'policyDescription',
            'action_set_key': 'actionSetKey',
            'allow_conditions': 'allowConditions',
            'resource_condition_node': 'resourceConditionNode',
            'named_resources': 'namedResources',
            'resource_condition': 'resourceCondition',
            'action_set': 'actionSet'
        }

        self._id = None
        self._domain = None
        self._entity_name = None
        self._policy_name = None
        self._policy_description = None
        self._action_set_key = None
        self._allow_conditions = None
        self._resource_condition_node = None
        self._named_resources = None
        self._resource_condition = None
        self._action_set = None

    @property
    def id(self):
        """
        Gets the id of this ResourcePermissionPolicy.


        :return: The id of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this ResourcePermissionPolicy.


        :param id: The id of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._id = id

    @property
    def domain(self):
        """
        Gets the domain of this ResourcePermissionPolicy.


        :return: The domain of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._domain

    @domain.setter
    def domain(self, domain):
        """
        Sets the domain of this ResourcePermissionPolicy.


        :param domain: The domain of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._domain = domain

    @property
    def entity_name(self):
        """
        Gets the entity_name of this ResourcePermissionPolicy.


        :return: The entity_name of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._entity_name

    @entity_name.setter
    def entity_name(self, entity_name):
        """
        Sets the entity_name of this ResourcePermissionPolicy.


        :param entity_name: The entity_name of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._entity_name = entity_name

    @property
    def policy_name(self):
        """
        Gets the policy_name of this ResourcePermissionPolicy.


        :return: The policy_name of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._policy_name

    @policy_name.setter
    def policy_name(self, policy_name):
        """
        Sets the policy_name of this ResourcePermissionPolicy.


        :param policy_name: The policy_name of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._policy_name = policy_name

    @property
    def policy_description(self):
        """
        Gets the policy_description of this ResourcePermissionPolicy.


        :return: The policy_description of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._policy_description

    @policy_description.setter
    def policy_description(self, policy_description):
        """
        Sets the policy_description of this ResourcePermissionPolicy.


        :param policy_description: The policy_description of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._policy_description = policy_description

    @property
    def action_set_key(self):
        """
        Gets the action_set_key of this ResourcePermissionPolicy.


        :return: The action_set_key of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._action_set_key

    @action_set_key.setter
    def action_set_key(self, action_set_key):
        """
        Sets the action_set_key of this ResourcePermissionPolicy.


        :param action_set_key: The action_set_key of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._action_set_key = action_set_key

    @property
    def allow_conditions(self):
        """
        Gets the allow_conditions of this ResourcePermissionPolicy.


        :return: The allow_conditions of this ResourcePermissionPolicy.
        :rtype: bool
        """
        return self._allow_conditions

    @allow_conditions.setter
    def allow_conditions(self, allow_conditions):
        """
        Sets the allow_conditions of this ResourcePermissionPolicy.


        :param allow_conditions: The allow_conditions of this ResourcePermissionPolicy.
        :type: bool
        """
        
        self._allow_conditions = allow_conditions

    @property
    def resource_condition_node(self):
        """
        Gets the resource_condition_node of this ResourcePermissionPolicy.


        :return: The resource_condition_node of this ResourcePermissionPolicy.
        :rtype: ResourceConditionNode
        """
        return self._resource_condition_node

    @resource_condition_node.setter
    def resource_condition_node(self, resource_condition_node):
        """
        Sets the resource_condition_node of this ResourcePermissionPolicy.


        :param resource_condition_node: The resource_condition_node of this ResourcePermissionPolicy.
        :type: ResourceConditionNode
        """
        
        self._resource_condition_node = resource_condition_node

    @property
    def named_resources(self):
        """
        Gets the named_resources of this ResourcePermissionPolicy.


        :return: The named_resources of this ResourcePermissionPolicy.
        :rtype: list[str]
        """
        return self._named_resources

    @named_resources.setter
    def named_resources(self, named_resources):
        """
        Sets the named_resources of this ResourcePermissionPolicy.


        :param named_resources: The named_resources of this ResourcePermissionPolicy.
        :type: list[str]
        """
        
        self._named_resources = named_resources

    @property
    def resource_condition(self):
        """
        Gets the resource_condition of this ResourcePermissionPolicy.


        :return: The resource_condition of this ResourcePermissionPolicy.
        :rtype: str
        """
        return self._resource_condition

    @resource_condition.setter
    def resource_condition(self, resource_condition):
        """
        Sets the resource_condition of this ResourcePermissionPolicy.


        :param resource_condition: The resource_condition of this ResourcePermissionPolicy.
        :type: str
        """
        
        self._resource_condition = resource_condition

    @property
    def action_set(self):
        """
        Gets the action_set of this ResourcePermissionPolicy.


        :return: The action_set of this ResourcePermissionPolicy.
        :rtype: list[str]
        """
        return self._action_set

    @action_set.setter
    def action_set(self, action_set):
        """
        Sets the action_set of this ResourcePermissionPolicy.


        :param action_set: The action_set of this ResourcePermissionPolicy.
        :type: list[str]
        """
        
        self._action_set = action_set

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

