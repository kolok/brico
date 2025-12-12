# Generated migration for Role model and role FK in OrganizationMember

from django.db import migrations, models
import django.db.models.deletion


def create_default_roles(apps, schema_editor):
    """Create the three default roles: administrator, writer, reader."""
    Role = apps.get_model('organization', 'Role')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    # Get ContentTypes for our models
    project_ct = ContentType.objects.get(app_label='organization', model='project')
    resource_ct = ContentType.objects.get(app_label='organization', model='resource')
    
    # Create Administrator role with all permissions
    admin_role, _ = Role.objects.get_or_create(
        name='administrator',
        defaults={'description': 'Full access to all organization resources'}
    )
    admin_permissions = Permission.objects.filter(
        content_type__in=[project_ct, resource_ct]
    )
    admin_role.permissions.set(admin_permissions)
    
    # Create Writer role with add/change/delete permissions
    writer_role, _ = Role.objects.get_or_create(
        name='writer',
        defaults={'description': 'Can create, edit and delete resources'}
    )
    writer_permissions = Permission.objects.filter(
        content_type__in=[project_ct, resource_ct],
        codename__in=[
            'add_project', 'change_project', 'delete_project', 'view_project',
            'add_resource', 'change_resource', 'delete_resource', 'view_resource'
        ]
    )
    writer_role.permissions.set(writer_permissions)
    
    # Create Reader role with view-only permissions
    reader_role, _ = Role.objects.get_or_create(
        name='reader',
        defaults={'description': 'Read-only access to resources'}
    )
    reader_permissions = Permission.objects.filter(
        content_type__in=[project_ct, resource_ct],
        codename__in=['view_project', 'view_resource']
    )
    reader_role.permissions.set(reader_permissions)


def assign_default_role_to_existing_members(apps, schema_editor):
    """Assign administrator role to all existing organization members."""
    OrganizationMember = apps.get_model('organization', 'OrganizationMember')
    Role = apps.get_model('organization', 'Role')
    
    try:
        admin_role = Role.objects.get(name='administrator')
        OrganizationMember.objects.filter(role__isnull=True).update(role=admin_role)
    except Role.DoesNotExist:
        pass  # Will be handled by create_default_roles


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_alter_organization_description_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        # Create Role model
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('administrator', 'Administrator'), ('writer', 'Writer'), ('reader', 'Reader')], max_length=50, unique=True, verbose_name='Role name')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('permissions', models.ManyToManyField(blank=True, related_name='roles', to='auth.permission', verbose_name='Permissions')),
            ],
            options={
                'verbose_name': 'Role',
                'verbose_name_plural': 'Roles',
                'ordering': ['name'],
            },
        ),
        # Add role FK to OrganizationMember (nullable first)
        migrations.AddField(
            model_name='organizationmember',
            name='role',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='members',
                to='organization.role',
                verbose_name='Role',
                help_text="User's role in this organization"
            ),
        ),
        # Populate default roles
        migrations.RunPython(create_default_roles, migrations.RunPython.noop),
        # Assign default role to existing members
        migrations.RunPython(assign_default_role_to_existing_members, migrations.RunPython.noop),
        # Make role field required
        migrations.AlterField(
            model_name='organizationmember',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='members',
                to='organization.role',
                verbose_name='Role',
                help_text="User's role in this organization"
            ),
        ),
        # Update Meta
        migrations.AlterModelOptions(
            name='organizationmember',
            options={
                'verbose_name': 'Organization Member',
                'verbose_name_plural': 'Organization Members'
            },
        ),
    ]
