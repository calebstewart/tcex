"""Indicator_Attribute TQL Filter"""
# standard library
from enum import Enum

# first-party
from tcex.api.tc.v3.api_endpoints import ApiEndpoints
from tcex.api.tc.v3.filter_abc import FilterABC
from tcex.api.tc.v3.tql.tql import Tql
from tcex.api.tc.v3.tql.tql_operator import TqlOperator
from tcex.api.tc.v3.tql.tql_type import TqlType


class IndicatorAttributeFilter(FilterABC):
    """Filter Object for IndicatorAttributes"""

    @property
    def _api_endpoint(self) -> str:
        """Return the API endpoint."""
        return ApiEndpoints.INDICATOR_ATTRIBUTES.value

    def date_added(self, operator: Enum, date_added: str) -> None:
        """Filter Date Added based on **dateAdded** keyword.

        Args:
            operator: The operator enum for the filter.
            date_added: The date the attribute was added to the system.
        """
        self._tql.add_filter('dateAdded', operator, date_added, TqlType.STRING)

    def date_val(self, operator: Enum, date_val: str) -> None:
        """Filter Date based on **dateVal** keyword.

        Args:
            operator: The operator enum for the filter.
            date_val: The date value of the attribute (only applies to certain types).
        """
        self._tql.add_filter('dateVal', operator, date_val, TqlType.STRING)

    def displayed(self, operator: Enum, displayed: bool) -> None:
        """Filter Displayed based on **displayed** keyword.

        Args:
            operator: The operator enum for the filter.
            displayed: Whether or not the attribute is displayed on the item.
        """
        self._tql.add_filter('displayed', operator, displayed, TqlType.BOOLEAN)

    @property
    def has_indicator(self):
        """Return **IndicatorFilter** for further filtering."""
        # first-party
        from tcex.api.tc.v3.indicators.indicator_filter import IndicatorFilter

        indicators = IndicatorFilter(Tql())
        self._tql.add_filter('hasIndicator', TqlOperator.EQ, indicators, TqlType.SUB_QUERY)
        return indicators

    def has_security_label(self, operator: Enum, has_security_label: int) -> None:
        """Filter Associated Security Label based on **hasSecurityLabel** keyword.

        Args:
            operator: The operator enum for the filter.
            has_security_label: A nested query for association to other security labels.
        """
        self._tql.add_filter('hasSecurityLabel', operator, has_security_label, TqlType.INTEGER)

    def id(self, operator: Enum, id: int) -> None:  # pylint: disable=redefined-builtin
        """Filter ID based on **id** keyword.

        Args:
            operator: The operator enum for the filter.
            id: The ID of the attribute.
        """
        self._tql.add_filter('id', operator, id, TqlType.INTEGER)

    def indicator_id(self, operator: Enum, indicator_id: int) -> None:
        """Filter Indicator ID based on **indicatorId** keyword.

        Args:
            operator: The operator enum for the filter.
            indicator_id: The ID of the indicator the indicator attribute is applied to.
        """
        self._tql.add_filter('indicatorId', operator, indicator_id, TqlType.INTEGER)

    def int_val(self, operator: Enum, int_val: int) -> None:
        """Filter Integer Value based on **intVal** keyword.

        Args:
            operator: The operator enum for the filter.
            int_val: The integer value of the attribute (only applies to certain types).
        """
        self._tql.add_filter('intVal', operator, int_val, TqlType.INTEGER)

    def last_modified(self, operator: Enum, last_modified: str) -> None:
        """Filter Last Modified based on **lastModified** keyword.

        Args:
            operator: The operator enum for the filter.
            last_modified: The date the attribute was last modified in the system.
        """
        self._tql.add_filter('lastModified', operator, last_modified, TqlType.STRING)

    def max_size(self, operator: Enum, max_size: int) -> None:
        """Filter Max Size based on **maxSize** keyword.

        Args:
            operator: The operator enum for the filter.
            max_size: The max length of the attribute text.
        """
        self._tql.add_filter('maxSize', operator, max_size, TqlType.INTEGER)

    def owner(self, operator: Enum, owner: int) -> None:
        """Filter Owner ID based on **owner** keyword.

        Args:
            operator: The operator enum for the filter.
            owner: The owner ID of the attribute.
        """
        self._tql.add_filter('owner', operator, owner, TqlType.INTEGER)

    def owner_name(self, operator: Enum, owner_name: str) -> None:
        """Filter Owner Name based on **ownerName** keyword.

        Args:
            operator: The operator enum for the filter.
            owner_name: The owner name of the attribute.
        """
        self._tql.add_filter('ownerName', operator, owner_name, TqlType.STRING)

    def source(self, operator: Enum, source: str) -> None:
        """Filter Source based on **source** keyword.

        Args:
            operator: The operator enum for the filter.
            source: The source text of the attribute.
        """
        self._tql.add_filter('source', operator, source, TqlType.STRING)

    def text(self, operator: Enum, text: str) -> None:
        """Filter Text based on **text** keyword.

        Args:
            operator: The operator enum for the filter.
            text: The text of the attribute (only applies to certain types).
        """
        self._tql.add_filter('text', operator, text, TqlType.STRING)

    def type(self, operator: Enum, type: int) -> None:  # pylint: disable=redefined-builtin
        """Filter Type ID based on **type** keyword.

        Args:
            operator: The operator enum for the filter.
            type: The ID of the attribute type.
        """
        self._tql.add_filter('type', operator, type, TqlType.INTEGER)

    def type_name(self, operator: Enum, type_name: str) -> None:
        """Filter Type Name based on **typeName** keyword.

        Args:
            operator: The operator enum for the filter.
            type_name: The name of the attribute type.
        """
        self._tql.add_filter('typeName', operator, type_name, TqlType.STRING)

    def user(self, operator: Enum, user: str) -> None:
        """Filter User based on **user** keyword.

        Args:
            operator: The operator enum for the filter.
            user: The user who created the attribute.
        """
        self._tql.add_filter('user', operator, user, TqlType.STRING)
