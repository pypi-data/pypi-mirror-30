# -*- coding: utf-8 -*-
from . import helpers
import requests


class Analysis:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/animal/'

    def get_analysis_summery(self, team_id, project_id):
        url = self.endpoint + self.url + 'getLatestAnalysisSummary?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_analysis(self, team_id, project_id, analysis_id):
        url = self.endpoint + self.url + 'getAnalysis?team_id=%s&project_id=%s&id=%s' % (team_id, project_id, analysis_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Projects:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/project/'

    def get_projects(self, team_id):
        url = self.endpoint + self.url + 'getProjects?team_id=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_project(self, team_id, project_id):
        url = self.endpoint + self.url + 'getProject?team_id=%s&id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Rulesets:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/ruleset/'

    def get_rulesets(self, team_id):
        url = self.endpoint + self.url + 'getRulesets?team_id=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_ruleset(self, team_id, ruleset_id):
        url = self.endpoint + self.url + 'getRuleset?team_id=%s&id=%s' % (team_id, ruleset_id)
        return requests.get(url, headers={"authorization": self.token}).json()

    def get_applied_ruleset_for_project(self, team_id, project_id):
        url = self.endpoint + self.url + 'getAppliedRulesetForProject?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.get(url, headers={"authorization": self.token}).json()


class Scanner:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/scanner/'

    def analyze_project(self, team_id, project_id):
        url = self.endpoint + self.url + 'analyzeProject?team_id=%s&project_id=%s' % (team_id, project_id)
        return requests.post(url, headers={"authorization": self.token}).json()

    def get_analysis_status(self, team_id, project_id, analysis_id):
        url = self.endpoint + '/v1/scanner/getAnalysisStatus?team_id=%s&project_id=%s&id=%s' % (team_id, project_id, analysis_id)
        res = requests.get(url, headers={"authorization": self.token})
        return res.json()


class Teams:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/teams/'

    def get_team(self, team_id):
        """Gets a teams info"""
        url = self.endpoint + self.url + 'getTeam?someid=%s' % team_id
        return requests.get(url, headers={"authorization": self.token}).json()


class Users:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/users/'

    def get_self(self):
        url = self.endpoint + self.url + 'getSelf'
        return requests.get(url, headers={"authorization": self.token}).json()


class Vulnerability:
    def __init__(self):
        self.token = helpers.get_envvars()
        self.endpoint = helpers.get_api_endpoint()
        self.url = '/v1/vulnerability/'

    def get_products(self, external_id):
        url = self.endpoint + self.url + 'getProducts?external_id=%s' % external_id
        return requests.get(url).json()

    def get_vulnerabilities(self, product, version):
        url = self.endpoint + self.url + 'getVulnerabilities?product=%s&version=%s' % (product, version)
        return requests.get(url).json()

    def get_vulnerability(self, external_id):
        url = self.endpoint + self.url + 'getVulnerability?external_id=%s' % external_id
        return requests.get(url).json()
