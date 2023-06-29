import logging
import requests
import yaml
from django.conf import settings
from urllib.parse import urlparse

logger = logging.Logger('log')


def collect_projects():
    """get all projects by OPS api"""
    logger.info('Start to collect projects')
    url = settings.OPS_SOURCE_URL
    token = get_token()
    headers = {'Authorization': 'Bearer {}'.format(token)}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        logger.error('Fail to update projects.')
        return
    res = []
    projects = r.json().get('data')
    for project in projects:
        url = project.get('repository')
        if url.endswith('.git'):
            url = url[:-4]
        if not is_valid_project(url):
            continue
        branch = project.get('branch')
        maintainer = project.get('developer')
        email = project.get('email')
        data = {
            'url': url,
            'branch': branch,
            'maintainer': maintainer,
            'email': email
        }
        res.append(data)
    logger.info('All infrastructure projects have been collected: total {}'.format(len(res)))
    return res


def get_token():
    """get authentication token of OPS"""
    url = settings.OPS_AUTH_URL
    data = {
        'username': settings.OPS_USERNAME,
        'password': settings.OPS_PASSWORD
    }
    r = requests.post(url, data=data)
    if r.status_code != 200:
        logger.error('Fail to get token.')
        return
    token = r.json().get('token')
    logger.info('Get OPS token successfully.')
    return token


def is_valid_project(url):
    """check validation of a project by its url"""
    valid_projects_conf = settings.VALID_PROJECTS_CONF
    with open(valid_projects_conf, 'r') as f:
        valid_projects = yaml.safe_load(f)
    valid_domains = valid_projects.get('valid_domains')
    valid_organizations = valid_projects.get('valid_organizations')
    parser = urlparse(url) 
    domain = parser.netloc
    if domain not in valid_domains:
        return False
    organization = parser.path.split('/')[1]
    if organization in valid_organizations:
        return True
    else:
        return False
