"""
A Python client for interacting with the Center for Responsive Politics'
campaign finance data.

API docs: https://www.opensecrets.org/resources/create/api_doc.php
"""

import json
import os

import requests

try:
    import urllib.parse as urllib
except ImportError:
    import urllib as urllib

from .exceptions import CRPError


class Client(object):
    """
    The Client class handles retrieving and parsing responses from the
    OpenSecrets.org API.

    """

    def __init__(self, apikey=None):
        self.apikey = apikey

    def _set_payload(self, method, params):
        params = params.copy()
        params.update({'apikey': self.apikey, "output":"json", "method": method})
        return params

    def fetch(self, method, **params):
        request_str = "https://www.opensecrets.org/api/"
        payload = self._set_payload(method, params)
        response = requests.get(request_str, params=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            raise CRPError(method, response, response.url)

class CandidatesClient(Client):
    """
    Retrieves and parses information pertaining to current Congressional
    legislators.
    """

    def get(self, id_code):
        """
            id_code may be either a candidate's specific CID, or a two letter
            state code, or a four character district code.
        """
        return self.fetch('getLegislators', id=id_code)['legislator']

    def pfd(self, cid, year=None):
        kwargs = {'cid' : cid}

        if year:
            kwargs['year'] = year

        return self.fetch('memPFDprofile', **kwargs)['member_profile']

    def summary(self, cid, cycle=None):
        kwargs = {'cid' : cid}

        if cycle:
            kwargs['cycle'] = cycle

        return self.fetch('candSummary', **kwargs)['summary']['@attributes']

    def contrib(self, cid, cycle=None):
        kwargs = {'cid' : cid}

        if cycle:
            kwargs['cycle'] = cycle

        return self.fetch('candContrib', **kwargs)['contributors']['contributor']

    def industries(self, cid, cycle=None):
        kwargs = {'cid' : cid}

        if cycle:
            kwargs['cycle'] = cycle

        return self.fetch('candIndustry', **kwargs)['industries']['industry']

    def contrib_by_ind(self, cid, industry, cycle=None):
        kwargs = {'cid' : cid, 'ind' : industry}

        if cycle:
            kwargs['cycle'] = cycle

        return self.fetch('candIndByInd', **kwargs)['candIndus']['@attributes']

    def sector(self, cid, cycle=None):
        kwargs = {'cid' : cid}

        if cycle:
            kwargs['cycle'] = cycle

        return self.fetch('candSector', **kwargs)['sectors']['sector']


class CommitteesClient(Client):
    """
    Retrieves and parses fundraising information pertaining to Congressional
    committees.
    """

    def cmte_by_ind(self, cmte, industry, congress=None):
        kwargs = {'cmte' : cmte, 'indus' : industry}

        if congress:
            kwargs['congno'] = congress

        return self.fetch('congCmteIndus', **kwargs)['committee']['member']


class OrganizationsClient(Client):
    """
    Retrieves and parses information pertaining to fundraising
    organizations.
    """

    def get(self, org_name):
        return self.fetch('getOrgs', org=org_name)['organization']

    def summary(self, org_id):
        return self.fetch('orgSummary', id=org_id)['organization']['@attributes']


class IndependentExpendituresClient(Client):
    """
    Retrieves and parses information regarding independent expenditure
    transactions.
    """

    def get(self):
        return self.fetch('independentExpend')['indexp']


class CRP(Client):
    """
    The public interface for the OpenSecrets.org API.

    Methods are namespaced by topic. Responses are returned as decoded JSON
    and trimmed for ease of use.

    An OpenSecrets.org API key is required, which can be passed as an argument
    when creating a new instance, or included as an environment variable.
    """

    def __init__(self, apikey=None):

        if apikey is None:
            apikey = os.environ.get('OPENSECRETS_API_KEY')

        if not apikey:
            raise CRPError("Most Provide An Opensecrets API Key")

        super(CRP, self).__init__(apikey)
        self.candidates = CandidatesClient(self.apikey)
        self.committees = CommitteesClient(self.apikey)
        self.orgs = OrganizationsClient(self.apikey)
        self.indexp = IndependentExpendituresClient(self.apikey)
