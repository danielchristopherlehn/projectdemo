from django.db import migrations


def sync_glossary_editor_permissions(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, _ = Group.objects.get_or_create(name="Glossary Editors")
    permissions = Permission.objects.filter(
        content_type__app_label="main",
        codename__in=[
            "view_glossaryterm",
            "add_glossaryterm",
            "change_glossaryterm",
            "manage_glossary",
        ],
    )
    group.permissions.set(permissions)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_create_glossary_editors_group"),
    ]

    operations = [
        migrations.RunPython(sync_glossary_editor_permissions, migrations.RunPython.noop),
    ]
