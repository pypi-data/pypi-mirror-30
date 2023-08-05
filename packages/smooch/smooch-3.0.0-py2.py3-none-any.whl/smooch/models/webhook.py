# coding: utf-8

"""
    Smooch

    The Smooch API is a unified interface for powering messaging in your customer experiences across every channel. Our API speeds access to new markets, reduces time to ship, eliminates complexity, and helps you build the best experiences for your customers. For more information, visit our [official documentation](https://docs.smooch.io).

    OpenAPI spec version: 3.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class Webhook(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, id=None, target=None, triggers=None, secret=None):
        """
        Webhook - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'id': 'str',
            'target': 'str',
            'triggers': 'list[str]',
            'secret': 'str'
        }

        self.attribute_map = {
            'id': '_id',
            'target': 'target',
            'triggers': 'triggers',
            'secret': 'secret'
        }

        self._id = None
        self._target = None
        self._triggers = None
        self._secret = None

        # TODO: let required properties as mandatory parameter in the constructor.
        #       - to check if required property is not None (e.g. by calling setter)
        #       - ApiClient.__deserialize_model has to be adapted as well
        if id is not None:
          self.id = id
        if target is not None:
          self.target = target
        if triggers is not None:
          self.triggers = triggers
        if secret is not None:
          self.secret = secret

    @property
    def id(self):
        """
        Gets the id of this Webhook.
        The webhook ID, generated automatically.

        :return: The id of this Webhook.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Sets the id of this Webhook.
        The webhook ID, generated automatically.

        :param id: The id of this Webhook.
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")

        self._id = id

    @property
    def target(self):
        """
        Gets the target of this Webhook.
        URL to be called when the webhook is triggered.

        :return: The target of this Webhook.
        :rtype: str
        """
        return self._target

    @target.setter
    def target(self, target):
        """
        Sets the target of this Webhook.
        URL to be called when the webhook is triggered.

        :param target: The target of this Webhook.
        :type: str
        """
        if target is None:
            raise ValueError("Invalid value for `target`, must not be `None`")

        self._target = target

    @property
    def triggers(self):
        """
        Gets the triggers of this Webhook.
        An array of triggers you wish to have the webhook listen to. If unspecified the default trigger is *message*.

        :return: The triggers of this Webhook.
        :rtype: list[str]
        """
        return self._triggers

    @triggers.setter
    def triggers(self, triggers):
        """
        Sets the triggers of this Webhook.
        An array of triggers you wish to have the webhook listen to. If unspecified the default trigger is *message*.

        :param triggers: The triggers of this Webhook.
        :type: list[str]
        """
        if triggers is None:
            raise ValueError("Invalid value for `triggers`, must not be `None`")

        self._triggers = triggers

    @property
    def secret(self):
        """
        Gets the secret of this Webhook.
        Secret which will be transmitted with each webhook invocation and can be used to verify the authenticity of the caller.

        :return: The secret of this Webhook.
        :rtype: str
        """
        return self._secret

    @secret.setter
    def secret(self, secret):
        """
        Sets the secret of this Webhook.
        Secret which will be transmitted with each webhook invocation and can be used to verify the authenticity of the caller.

        :param secret: The secret of this Webhook.
        :type: str
        """
        if secret is None:
            raise ValueError("Invalid value for `secret`, must not be `None`")

        self._secret = secret

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
        if not isinstance(other, Webhook):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
