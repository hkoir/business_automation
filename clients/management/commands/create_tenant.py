
from django_tenants.management.commands.create_tenant import Command as BaseCommand
from clients.models import Client, Domain

class Command(BaseCommand):
    def handle(self, *args, **kwargs): 
        schema_name = kwargs.get('schema_name')
        name = kwargs.get('name')
        domain_name = kwargs.get('domain_name')

        try:
            tenant = Client(schema_name=schema_name, name=name)
            tenant.save()
            domain = Domain(domain=domain_name, tenant=tenant, is_primary=True)
            domain.save()

            self.stdout.write(f"Tenant '{schema_name}' created successfully.")
        except Exception as e:
            self.stderr.write(f"Error creating tenant: {str(e)}")
