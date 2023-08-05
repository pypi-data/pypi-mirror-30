from pprint import pformat
from typing import TypeVar, Type
from six import iteritems
from ..util import deserialize_model

T = TypeVar('T')


class Model(object):
    bl_types = {}

    # attributeMap: The key is attribute name and the value is json key in definition.
    attribute_map = {}

    @classmethod
    def from_dict(cls, dikt):
        """
        Returns the dict as a model
        """
        return deserialize_model(dikt, cls)
    # from_dict.__annotations__ = {'cls': Type[T], 'return': T}

    def to_dict(self):
        """
        Returns the model properties as a dict

        :rtype: dict
        """
        result = {}

        for attr, _ in iteritems(self.bl_types):
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

        :rtype: str
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