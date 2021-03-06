from datetime import datetime, timedelta

import vcr
from rest_framework.test import APITestCase

from elections.tests.factories import (ElectionFactory, )


class TestElectionAPIQueries(APITestCase):
    lat = 51.5010089365
    lon = -0.141587600123

    def test_election_endpoint(self):
        ElectionFactory(group=None)
        resp = self.client.get("/api/elections/")
        data = resp.json()

        assert len(data['results']) == 1
        assert data['results'][0]['election_id'] == \
            "local.place-name-0.2017-03-23"

    def test_election_endpoint_current(self):
        ElectionFactory(group=None, poll_open_date=datetime.today())
        ElectionFactory(
            group=None, poll_open_date=datetime.today() - timedelta(days=60))

        resp = self.client.get("/api/elections/?current")
        data = resp.json()

        assert len(data['results']) == 1
        assert data['results'][0]['election_id'] == \
            "local.place-name-1.2017-03-23"
        assert data['results'][0]['current'] == True


    def test_election_endpoint_future(self):
        ElectionFactory(
            group=None,
            poll_open_date=datetime.today(),
            election_id="local.place-name-future-election.2017-03-23")
        ElectionFactory(
            group=None, poll_open_date=datetime.today() - timedelta(days=1))

        resp = self.client.get("/api/elections/?future")
        data = resp.json()

        assert len(data['results']) == 1
        assert data['results'][0]['election_id'] == \
            "local.place-name-future-election.2017-03-23"

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_election_for_postcode.yaml')
    def test_election_endpoint_for_postcode(self):
        election_id = "local.place-name.2017-03-23"
        ElectionFactory(group=None, election_id=election_id)
        ElectionFactory(group=None, geography=None)
        resp = self.client.get("/api/elections/?postcode=SW1A1AA")
        data = resp.json()

        assert len(data['results']) == 1
        assert data['results'][0]['election_id'] == election_id

    @vcr.use_cassette(
        'fixtures/vcr_cassettes/test_election_for_bad_postcode.yaml')
    def test_election_endpoint_for_bad_postcode(self):
        election_id = "local.place-name.2017-03-23"
        ElectionFactory(group=None, election_id=election_id)
        ElectionFactory(group=None, geography=None)
        resp = self.client.get("/api/elections/?postcode=SW1A1AX")
        data = resp.json()

        assert data['detail'] == "Invalid postcode"

    def test_election_endpoint_for_lat_lng(self):
        election_id = "local.place-name.2017-03-23"
        ElectionFactory(group=None, election_id=election_id)
        ElectionFactory(group=None, geography=None)

        resp = self.client.get(
            "/api/elections/?coords=51.5010089365,-0.141587600123")
        data = resp.json()

        assert data['results'][0]['election_id'] == election_id
        assert len(data['results']) == 1
