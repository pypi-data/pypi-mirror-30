from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from perfieldperms.models import PerFieldPermission, PFPContentType
from perfieldperms.utils import list_fields_for_ctype


class Command(BaseCommand):
    """
    Used to pre-generate permissions for models. Sources models from the
    PFPContentType table, or from the setting PFP_MODELS. If both
    sources are configured merges the lists.
    
    For each model listed gets a list of model level permissions, and for each
    model level perm generates a set of perfield permissions corresponding to
    each field on the model. These permissions take the form:
    <model-level-codename>__<field-name>

    If fields have been changed permissions are added/removed as appropriate.

    If you want to exclude a model level permissions add it to the setting
    PFP_IGNOREPERMS.

    Settings:
    PFP_MODELS -- an iterable of two tuples (app_label, model name) of models
            you want pfps created for.
    PFP_IGNORE_PERMS -- a dict of dicts of iterables of permissions you want
            ignored when creating pfps. Structured:
            {app_label:
                {model name: [<perm codename>, <perm codename>,..]}
            }
    PFP_IGNORE_DELETE -- By default perfieldperms doesn't create field level
            delete permissions as this doesn't necessarily make sense. Set to
            False if you want to create delete pfps.
    """
    help = 'Generates permissions for fields on selected models.'
    requires_migrations_checks = True

    def _get_perms(self, ctype):
        app_label = ctype.app_label
        model = ctype.model
        perms = Permission.objects.filter(
                content_type=ctype,
                perfieldpermission__isnull=True,
                )
        if (not hasattr(settings, 'PFP_IGNORE_DELETE') 
                or settings.PFP_IGNORE_DELETE):
            del_codename = 'delete_{}'.format(model)
            perms = perms.exclude(codename=del_codename)
        return perms

    def handle(self, *args, **options):
        # Get all the models to create permissions for
        models = set()
        if hasattr(settings, 'PFP_MODELS'):
            models.update(set(settings.PFP_MODELS))
        model_ctypes = ContentType.objects.filter(
                pfpcontenttype__isnull=False)
        models.update(set(
            [(ctype.app_label, ctype.model) for ctype in model_ctypes]
            ))

        deleted = 0
        existing = 0
        added = 0
        for app_label, model in models:
            ignore_perms = []
            if (hasattr(settings, 'PFP_IGNORE_PERMS')
                    and app_label in settings.PFP_IGNORE_PERMS
                    and model in settings.PFP_IGNORE_PERMS[app_label]):
                ignore_perms = settings.PFP_IGNORE_PERMS[app_label][model]

            ctype = ContentType.objects.get(app_label=app_label, model=model)
            model_fields = set(
                    [field for field, name in list_fields_for_ctype(ctype)]
                    )
            perms = self._get_perms(ctype)
            # Remove perms for removed fields, add permissions for new fields
            for perm in perms:
                pfps = PerFieldPermission.objects.filter(
                        model_permission=perm)

                if perm.codename in ignore_perms:
                    if settings.DEBUG:
                        for pfp in pfps:
                            self.stdout.write('Deleted permission {} for '
                                    'ignored permission {}.{} - {}'.format(
                                        pfp.codename,
                                        app_label,
                                        model,
                                        pfp.field_name
                                        )
                                    )
                    if pfps:
                        # pfps are a multi-table subclass so divide by 2 to get
                        # 'actual' number deleted
                        deleted += pfps.delete()[0] / 2
                else:
                    with transaction.atomic():
                        fields = model_fields.copy()
                        pfps = set(pfps)
                        existing += len(pfps)
                        while pfps:
                            pfp = pfps.pop()
                            if pfp.field_name in fields:
                                fields.remove(pfp.field_name)
                            else:
                                pfp.delete()
                                deleted += 1
                                if settings.DEBUG:
                                    self.stdout.write('Deleted permission {} '
                                            'for removed field {}.{} - {}'.format(
                                                pfp.codename,
                                                app_label,
                                                model, 
                                                pfp.field_name
                                                )
                                            )
                        for field in fields:
                            new_pfp = PerFieldPermission(
                                    content_type=ctype,
                                    codename='{}__{}'.format(perm.codename,
                                        field),
                                    name='{} - {}'.format(perm.name, field),
                                    field_name=field,
                                    model_permission=perm,
                                    )
                            new_pfp.full_clean()
                            new_pfp.save()
                            added += 1
                            if settings.DEBUG:
                                self.stdout.write('Added new permission {} '
                                'for field {}.{} - {}'.format(
                                            new_pfp.codename,
                                            app_label,
                                            model, 
                                            new_pfp.field_name
                                            )
                                        )
        self.stdout.write('Permissions added: {}\n'
                'Permissions deleted: {}\n'
                'Existing permissions skipped: {}'.format(added, deleted,
                    existing)
                )
