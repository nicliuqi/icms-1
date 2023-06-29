from django.core.management import BaseCommand
from cms.utils.kanban import generate_kanban_template
from cms.utils.packages import packages_map
from cms.utils.projects import collect_projects
from cms.utils.send_attention import receivers_statistics
from cms.utils.vulnerabilities import collect_infra_vulnerabilities


class Command(BaseCommand):
    def handle(self, *args, **options):
        projects = collect_projects()
        packages = packages_map()
        collect_infra_vulnerabilities(projects, packages)
        generate_kanban_template()
        receivers_statistics()
