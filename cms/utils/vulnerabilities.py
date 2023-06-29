import logging
import requests
from django.conf import settings
from cms.models import Vulnerability
from cms.utils.packages import wrap_project

logger = logging.getLogger('log')


def collect_vtopia_vulnerabilities():
    """get all known vulnerabilities"""
    logger.info('Start to collect all vulnerabilities')
    res = []
    page = 1
    while True:
        url = settings.CVE_SOURCE_URL
        params = {
            'page_num': page,
            'count_per_page': 100
        }
        r = requests.get(url, params=params)
        if r.status_code != 200:
            print('Fail to get vulnerabilities data of page {}'.format(page))
            continue
        print('Get vulnerabilities data of page {}'.format(page))
        vul_list = r.json().get('body').get('list')
        if not vul_list:
            break
        for i in vul_list:
            res.append(i)
        page += 1
    logger.info('All Vtopia vulnerabilities have been collected: total {}'.format(len(res)))
    return res


def collect_infra_vulnerabilities(projects, packages):
    logger.info('Start to collect Infra vulnerabilities')
    vulnerabilities = collect_vtopia_vulnerabilities()
    print(len(vulnerabilities))
    vul_maps = {}
    for vul in vulnerabilities:
        cve_num = vul.get('cveNum')
        vul_maps[cve_num] = vul
    pack_names = []
    pkg_vul_maps = {}
    for vul in vulnerabilities:
        cve_num = vul.get('cveNum')
        pack_name = vul.get('packName')
        for pack in pack_name:
            if pack not in pack_names:
                pack_names.append(pack)
            if pack not in pkg_vul_maps.keys():
                pkg_vul_maps[pack] = []
            if cve_num not in pkg_vul_maps[pack]:
                pkg_vul_maps[pack].append(cve_num)
    projects_map = {}
    for project in projects:
        url = project.get('url')
        branch = project.get('branch')
        if branch:
            _, wrap_key = wrap_project(url, branch)
            projects_map[wrap_key] = project
    Vulnerability.objects.all().update(mark=0)
    for package in packages:
        if package not in pack_names:
            continue
        projects = packages[package]
        match_cve_nums = pkg_vul_maps[package]
        logger.info('match_package: {}, match_cv_nums: {}'.format(package, match_cve_nums))
        pkg_name, pkg_version = package.split('==')
        for project in projects:
            match_project = projects_map[project]
            url = match_project.get('url')
            branch = match_project.get('branch')
            maintainer = match_project.get('maintainer')
            email = match_project.get('email')
            for i in  match_cve_nums:
                cve = vul_maps[i]
                cve_num = cve.get('cveNum')
                cve_detail = '{}/{}'.format(settings.VUL_DETAIL_PREFIX, cve_num)
                if not Vulnerability.objects.filter(cve_num=cve_num,
                                                    cve_detail=cve_detail,
                                                    project_url=url,
                                                    project_branch=branch,
                                                    package=pkg_name,
                                                    version=pkg_version,
                                                    maintainer=maintainer,
                                                    email=email):
                    Vulnerability.objects.create(cve_num=cve_num,
                                                 cve_detail=cve_detail,
                                                 project_url=url,
                                                 project_branch=branch,
                                                 package=pkg_name,
                                                 version=pkg_version,
                                                 maintainer=maintainer,
                                                 email=email,
                                                 mark=1)
                else:
                    Vulnerability.objects.filter(cve_num=cve_num,
                                                 cve_detail=cve_detail,
                                                 project_url=url,
                                                 project_branch=branch,
                                                 package=pkg_name,
                                                 version=pkg_version,
                                                 maintainer=maintainer,
                                                 email=email).update(mark=1)
    Vulnerability.objects.filter(mark=0).delete()
    logger.info('Collect all Infra vulnerabilities: total {}'.format(len(Vulnerability.objects.all())))