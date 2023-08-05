# -*- coding: utf-8 -*-
from . import helpers
import requests


class Analysis:
    """
    The Analysis class interacts with endpoints to return Analysis data.
    Analysis data includes a scan against the project specified and the data
    returned is json formated.
    """

    def __init__(self):
        """Initializes Analysis class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/animal/'

    def get_analysis_summery(self, team_id, project_id):
        """Gets a summary of analysis against a team and project.

        :param str team_id: The team id for the team a user wants to lookup
        :param str project_id: The project id for the project in a team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getLatestAnalysisSummary?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_analysis(self, team_id, project_id, analysis_id):
        """Gets an analysis against a team and project.

        :param str team_id: The team id for the team a user wants to lookup
        :param str project_id: The project id for the project in a team a user wants to lookup
        :param str analysis_id: The analysis id for the analysis a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getAnalysis?team_id=%s&project_id=%s&id=%s' % (team_id, project_id, analysis_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Projects:
    """
    The Projects class interacts with endpoints to return Project data.
    Project data includes the project information specified and the data
    returned is json formated.
    """

    def __init__(self):
        """Initializes Projects class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/project/'

    def get_projects(self, team_id):
        """Gets projects for a team.

        :param str team_id: The team id for the team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getProjects?team_id=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_project(self, team_id, project_id):
        """Gets project for a team.

        :param str team_id: The team id for the team a user wants to lookup
        :param str project_id: The project id for the project in a team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getProject?team_id=%s&id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Rulesets:
    """
    The Rulesets class interacts with endpoints to return Ruleset data.
    Ruleset data includes the ruleset information specified and the data
    returned is json formated.
    """

    def __init__(self):
        """Initializes Rulesets class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/ruleset/'

    def get_rulesets(self, team_id):
        """Gets rulesets for a team.

        :param str team_id: The team id for the team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getRulesets?team_id=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_ruleset(self, team_id, ruleset_id):
        """Gets ruleset for a team.

        :param str team_id: The team id for the team a user wants to lookup
        :param str ruleset_id: The ruleset id for the ruleset in a team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getRuleset?team_id=%s&id=%s' % (team_id, ruleset_id)
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_applied_ruleset_for_project(self, team_id, project_id):
        """Gets applied ruleset for a project in a team.

        :param str team_id: The team id for the team a user wants to lookup
        :param str project_id: The project id for the project in a team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getAppliedRulesetForProject?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Scanner:
    """
    The Scanner class interacts with endpoints to return Scanner data as well
    as conduct scans. The data returned is json formated.
    """

    def __init__(self):
        """Initializes Scanner class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/scanner/'

    def analyze_project(self, team_id, project_id):
        """Starts an analysis against the given project and team.

        :param str team_id: The team id for the team a user wants to analyze
        :param str project_id: The project id for the project in a team a user wants to analyze
        :returns: A ``requests.post(url).json()`` instance
        """

        url = self.endpoint + self.url + 'analyzeProject?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.post(url, headers={"authorization": self.token}).json()

    def get_analysis_status(self, team_id, project_id, analysis_id):
        """Gets an analysis status for the specified analysis

        :param str team_id: The team id for the team a user wants to lookup
        :param str project_id: The project id for the project in a team a user wants to lookup
        :param str analysis_id: The analysis id for the analysis in a project a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + '/v1/scanner/getAnalysisStatus?team_id=%s&project_id=%s&id=%s' % (team_id, project_id, analysis_id)
        res = requests.get(url, headers={"authorization": self.token})
        return res.json()


class Teams:
    """
    The Teams class interacts with endpoints to return Teams data.
    The data returned is json formated.
    """

    def __init__(self):
        """Initializes Teams class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/teams/'

    def get_team(self, team_id):
        """Gets a teams info.

        :param str team_id: The team id for the team a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """
        url = self.endpoint + self.url + 'getTeam?someid=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()


class Users:
    """
    The Users class interacts with endpoints to return Users data.
    The data returned is json formated.
    """

    def __init__(self):
        """Initializes Users class with tokens and endpoint information."""

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/users/'

    def get_self(self):
        """Gets self info.

        :returns: A ``requests.get(url).json()`` instance
        """
        url = self.endpoint + self.url + 'getSelf'
        return requests.get(url, headers={"authorization": self.token}).json()


class Vulnerability:
    """
    The Vulnerability class interacts with endpoints to return Vulnerability
    data. The data returned is json formated.
    """

    def __init__(self):
        """Initializes Vulnerability class with tokens and endpoint information.
        """

        self.token = helpers.get_token()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/vulnerability/'

    def get_products(self, external_id):
        """Gets data on specified product.

        :param str external_id: The external id for the cpe a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getProducts?external_id=%s' % external_id
        return requests.get(url).json()

    def get_vulnerabilities(self, product, version=''):
        """Gets data on specified product and version if specified.

        :param str product: The product name for the user wants to lookup
        :param str version: The version number the user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getVulnerabilities?product=%s&version=%s&limit=1000' % (product, version)
        return requests.get(url).json()

    def get_vulnerability(self, external_id):
        """Gets data on specified CVE.

        :param str external_id: The external id for the cve a user wants to lookup
        :returns: A ``requests.get(url).json()`` instance
        """

        url = self.endpoint + self.url + 'getVulnerability?external_id=%s' % external_id
        return requests.get(url).json()
