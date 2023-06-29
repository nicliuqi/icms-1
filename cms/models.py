from django.db import models
  

class Vulnerability(models.Model):
    cve_num = models.CharField(verbose_name='CVE number', max_length=20)
    cve_detail = models.CharField(verbose_name='CVE detail', max_length=60)
    project_url = models.CharField(verbose_name='project address', max_length=200)
    project_branch = models.CharField(verbose_name='project branch', max_length=50)
    package = models.CharField(verbose_name='package', max_length=50)
    version = models.CharField(verbose_name='package version', max_length=50)
    maintainer = models.CharField(verbose_name='maintainer', max_length=100)
    email = models.CharField(verbose_name='maintainer email', max_length=100)
    mark = models.IntegerField(verbose_name='mark about whether updated', choices=((0, 'not marked'), (1, 'marked')),
            default=0)
