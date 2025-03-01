"""TcEx Framework Module"""

# standard library
import os
from datetime import datetime, timedelta
from typing import cast

# third-party
from _pytest.fixtures import FixtureRequest

# first-party
from tcex.api.tc.v2.threat_intelligence.mapping.group.group_type.campaign import Campaign
from tcex.tcex import TcEx
from tests.api.tc.v2.threat_intelligence.ti_helper import TestThreatIntelligence, TIHelper


class TestCampaignGroups(TestThreatIntelligence):
    """Test TcEx Campaign Groups."""

    group_type = 'Campaign'
    owner = os.getenv('TC_OWNER')
    tcex: TcEx

    def setup_method(self):
        """Configure setup before all tests."""
        self.ti_helper = TIHelper(self.group_type)
        self.ti = self.ti_helper.ti
        self.tcex = self.ti_helper.tcex

    def tests_ti_campaign_create(self):
        """Create a group using specific interface."""
        group_data = {
            'first_seen': datetime.now().isoformat(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.campaign(**group_data)
        r = ti.create()

        # assert response
        assert r.status_code == 201

        # retrieve group for asserts
        group_data['unique_id'] = ti.unique_id
        ti = self.ti.campaign(**group_data)
        r = ti.single()
        response_data = r.json()
        ti_data = response_data.get('data', {}).get(ti.api_entity)

        # validate response data
        assert r.status_code == 200
        assert response_data.get('status') == 'Success'

        # validate ti data
        assert ti_data.get(ti.api_entity) == group_data.get(ti.api_entity)

        # cleanup group
        r = ti.delete()
        assert r.status_code == 200

    def tests_ti_campaign_add_attribute(self, request: FixtureRequest):
        """Test group add attribute."""
        super().group_add_attribute(request)

    def tests_ti_campaign_add_label(self):
        """Test group add label."""
        super().group_add_label()

    def tests_ti_campaign_add_tag(self, request: FixtureRequest):
        """Test group add tag."""
        super().group_add_tag(request)

    def tests_ti_campaign_delete(self):
        """Test group delete."""
        super().group_delete()

    def tests_ti_campaign_get(self):
        """Test group get with generic group method."""
        super().group_get()

    def tests_ti_campaign_get_filter(self):
        """Test group get with filter."""
        super().group_get_filter()

    def tests_ti_campaign_get_includes(self, request: FixtureRequest):
        """Test group get with includes."""
        super().group_get_includes(request)

    def tests_ti_campaign_get_attribute(self, request: FixtureRequest):
        """Test group get attribute."""
        super().group_get_attribute(request)

    def tests_ti_campaign_get_label(self):
        """Test group get label."""
        super().group_get_label()

    def tests_ti_campaign_get_tag(self, request: FixtureRequest):
        """Test group get tag."""
        super().group_get_tag(request)

    def tests_ti_campaign_update(self, request: FixtureRequest):
        """Test updating group metadata."""
        super().group_update(request)

    #
    # Custom test cases
    #

    def tests_ti_campaign_first_seen(self):
        """Update first seen value."""
        helper_ti = cast(Campaign, self.ti_helper.create_group())

        # update first seen (coverage)
        first_seen = (datetime.now() - timedelta(days=2)).isoformat()
        r = helper_ti.first_seen(first_seen)
        assert r.status_code == 200

    def tests_ti_campaign_first_seen_no_update(self):
        """Test update on group with no id."""
        group_data = {
            'first_seen': datetime.now().isoformat(),
            'name': self.ti_helper.rand_name(),
            'owner': self.owner,
        }
        ti = self.ti.campaign(**group_data)

        # update first seen (coverage)
        try:
            first_seen = (datetime.now() - timedelta(days=2)).isoformat()
            ti.first_seen(first_seen)
            assert False, 'failed to catch group method call with no id.'
        except RuntimeError:
            assert True, 'caught group method call with no id'
