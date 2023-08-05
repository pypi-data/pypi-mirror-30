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


class LinkRequestResponseLinkRequests(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, integration_id=None, type=None, code=None, url=None):
        """
        LinkRequestResponseLinkRequests - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'integration_id': 'str',
            'type': 'str',
            'code': 'str',
            'url': 'str'
        }

        self.attribute_map = {
            'integration_id': 'integrationId',
            'type': 'type',
            'code': 'code',
            'url': 'url'
        }

        self._integration_id = None
        self._type = None
        self._code = None
        self._url = None

        # TODO: let required properties as mandatory parameter in the constructor.
        #       - to check if required property is not None (e.g. by calling setter)
        #       - ApiClient.__deserialize_model has to be adapted as well
        if integration_id is not None:
          self.integration_id = integration_id
        if type is not None:
          self.type = type
        if code is not None:
          self.code = code
        if url is not None:
          self.url = url

    @property
    def integration_id(self):
        """
        Gets the integration_id of this LinkRequestResponseLinkRequests.
        The integration ID.

        :return: The integration_id of this LinkRequestResponseLinkRequests.
        :rtype: str
        """
        return self._integration_id

    @integration_id.setter
    def integration_id(self, integration_id):
        """
        Sets the integration_id of this LinkRequestResponseLinkRequests.
        The integration ID.

        :param integration_id: The integration_id of this LinkRequestResponseLinkRequests.
        :type: str
        """
        if integration_id is None:
            raise ValueError("Invalid value for `integration_id`, must not be `None`")

        self._integration_id = integration_id

    @property
    def type(self):
        """
        Gets the type of this LinkRequestResponseLinkRequests.
        The integration type.

        :return: The type of this LinkRequestResponseLinkRequests.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """
        Sets the type of this LinkRequestResponseLinkRequests.
        The integration type.

        :param type: The type of this LinkRequestResponseLinkRequests.
        :type: str
        """
        if type is None:
            raise ValueError("Invalid value for `type`, must not be `None`")

        self._type = type

    @property
    def code(self):
        """
        Gets the code of this LinkRequestResponseLinkRequests.
        The link request code.

        :return: The code of this LinkRequestResponseLinkRequests.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """
        Sets the code of this LinkRequestResponseLinkRequests.
        The link request code.

        :param code: The code of this LinkRequestResponseLinkRequests.
        :type: str
        """
        if code is None:
            raise ValueError("Invalid value for `code`, must not be `None`")

        self._code = code

    @property
    def url(self):
        """
        Gets the url of this LinkRequestResponseLinkRequests.
        The link request url.

        :return: The url of this LinkRequestResponseLinkRequests.
        :rtype: str
        """
        return self._url

    @url.setter
    def url(self, url):
        """
        Sets the url of this LinkRequestResponseLinkRequests.
        The link request url.

        :param url: The url of this LinkRequestResponseLinkRequests.
        :type: str
        """
        if url is None:
            raise ValueError("Invalid value for `url`, must not be `None`")

        self._url = url

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
        if not isinstance(other, LinkRequestResponseLinkRequests):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
