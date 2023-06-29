from cms.models import Vulnerability
from cms.utils.packages import wrap_project

DIV_HEAD = '<div class="kanban" style="height: 100vh; display: flex; justify-content: center; align-items: center;' \
           'flex-direction: column">'
HEAD = '<h1>Kanban of Infra CVE</h1>'
NO_CVE = '<p><b>暂无CVE</b></p>'
DIV_TAIL = '</div>'


def merge_cves():
    vuls = Vulnerability.objects.all().values()
    tmp_dict = {}
    for vul in vuls:
        cve_num = vul.get('cve_num')
        cve_detail = vul.get('cve_detail')
        package = vul.get('package')
        version = vul.get('version')
        url = vul.get('project_url')
        branch = vul.get('project_branch')
        maintainer = vul.get('maintainer')
        data = {
            'cve_num': cve_num,
            'cve_detail': cve_detail,
            'package': package,
            'version': version,
            'url': url,
            'branch': branch,
            'maintainer': maintainer
        }
        _, wrap_key = wrap_project(url, branch)
        wrap_key += ':' + cve_num
        if wrap_key not in tmp_dict.keys():
            tmp_dict[wrap_key] = data
        else:
            target_data = tmp_dict[wrap_key]
            if target_data.get('maintainer') != maintainer:
                target_data['maintainer'] = ','.join([maintainer, target_data.get('maintainer')])
            tmp_dict[wrap_key] = target_data
    res = []
    for i in sorted(tmp_dict.keys()):
        res.append(tmp_dict[i])
    return res


def generate_kanban_template():
    div_head = DIV_HEAD
    head = HEAD
    no_cve = NO_CVE
    div_tail = DIV_TAIL
    cves = merge_cves()
    if not cves:
        body = div_head + head + no_cve + div_tail
        with open('cms/templates/index.html', 'w') as f:
            f.write(body)
        return
    table = '<table border="1" style="text-align:center">'
    table_header = """
    <tr>
        <th>CVE编号</th>
        <th>组件</th>
        <th>组件版本</th>
        <th>项目地址</th>
        <th>分支</th>
        <th>责任人</th>
    </tr>
    """
    table += table_header
    for cve in cves:
        cve_num = cve.get('cve_num')
        cve_detail = cve.get('cve_detail')
        url = cve.get('url')
        branch = cve.get('branch')
        package = cve.get('package')
        version = cve.get('version')
        maintainer = cve.get('maintainer')
        table += """
        <tr>
            <td><a href='{0}'>{1}</a></td>
            <td>{2}</td>
            <td>{3}</td>
            <td>{4}</td>
            <td>{5}</td>
            <td>{6}</td>
        </tr>
        """.format(cve_detail, cve_num, package, version, url, branch, maintainer)
    table += '</table>'
    body = div_head + head + table + div_tail
    with open('cms/templates/index.html', 'w') as f:
        f.write(body)
