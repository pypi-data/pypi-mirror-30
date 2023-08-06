from . import core
from datetime import datetime
from datetime import timedelta

"""
Reporting.py is a set of helper classes and functions to build reports using
Ion Channel. For the Report service see core.py
"""


class Projects:

    def get_projects_ids_from_team(self, team_id):
        projects = core.Projects()
        projects_list = projects.get_projects(team_id=team_id)['data']
        project_ids = []
        for project in projects_list:
            project_ids.append(project['id'])
        return project_ids

    def get_projects_ids_and_names_from_team(self, team_id):
        projects = core.Projects()
        projects_list = projects.get_projects(team_id=team_id)['data']
        project_info = []
        for project in projects_list:
            project_tuple = project['id'], project['name']
            project_info.append(project_tuple)
        return project_info

    def get_project_age(self, team_id, project_id):
        projects = core.Projects()
        project_created_at = datetime.strptime(
            projects.get_project(team_id=team_id,
                project_id=project_id)['data']['created_at'],
                    '%Y-%m-%dT%H:%M:%S.%fZ')
        time_between = datetime.now() - project_created_at
        return time_between

class Scanner:

    def get_virus_summary(self, team_id, project_id, analysis_id):
        analysis = core.Analysis()
        for summary in analysis.get_analysis(
            team_id=team_id,
            project_id=project_id,
            analysis_id=analysis_id
        )['data']['scan_summaries']:
            if 'virus' in summary['name']:
                return summary
            else:
                return {'virus_summary': None}


class Vulnerability:

    def get_highest_cve_for_product_version(self, product, version):
        vulnerability = core.Vulnerability()
        vulnerability_list = vulnerability.get_vulnerabilities(product=product, version=version)['data']
        cve_list = []
        for cve in vulnerability_list:
            cve_tuple = (cve['external_id'], cve['score'])
            cve_list.append(cve_tuple)
        sorted_by_score = sorted(cve_list, key=lambda tup: tup[1], reverse=True)
        highest_cve_id = sorted_by_score[0][0]
        return str(highest_cve_id)

    def get_sorted_list_cves_for_project_version(self, product, version):
        vulnerability = core.Vulnerability()
        vulnerability_list = vulnerability.get_vulnerabilities(product=product, version=version)['data']
        cve_list = []
        for cve in vulnerability_list:
            cve_tuple = (cve['external_id'], cve['score'])
            cve_list.append(cve_tuple)
        sorted_by_score = sorted(cve_list, key=lambda tup: tup[1], reverse=True)
        return sorted_by_score
