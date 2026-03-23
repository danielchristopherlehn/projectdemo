from django.db import migrations


def create_glossary_editors_group(apps, schema_editor):
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


def remove_glossary_editors_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name="Glossary Editors").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0003_alter_glossaryterm_options"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            create_glossary_editors_group,
            remove_glossary_editors_group,
        ),
    ]
