from django.conf import settings
from django.contrib.auth import get_permission_codename
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import title


def get_base_perm(content_type, obj):
    """Get a `Permission` based on a `ContentType` and model instance."""
    if obj is None or not hasattr(obj, 'pk') or obj.pk is None:
        codename = 'add_{}'.format(content_type.model)
    else:
        codename = 'change_{}'.format(content_type.model)

    return Permission.objects.select_related('content_type').get(
            content_type=content_type,
            codename=codename,
            )


def get_m2m_remote_fields(src_model, tgt_model):
    """
    Get a list of fields on `tgt_model` that are part of a m2m relationship
    from `src_model`.
    """
    return [
            field for field in src_model._meta.get_fields()
            if (field.is_relation
                and field.many_to_many
                and field.related_model == tgt_model)
            ]


def get_manager_name(src_model, tgt_model):
    """
    Get the name of the manager for an m2m relationship from `src_model` to
    `tgt_model`. Return `None` if there is no relationship.
    """
    fields = get_m2m_remote_fields(src_model, tgt_model)
    if fields:
        return fields[0].name
    return None


def get_non_pfp_perms(content_type):
    """Get all model level Permission objects for `content_type`."""
    return Permission.objects.filter(
            content_type=content_type,
            perfieldpermission__isnull=True,
            )


def list_fields_for_model(model):
    """
    Get a list of (name, verbose_name) tuples of concrete fields for `model`
    which is a subclass of django.db.models.Model.
    """
    return [
            (field.name, title(field.verbose_name)) for field in model._meta.get_fields()
            if field.concrete and (
                (not field.auto_created and field.editable)
                or (field.is_relation and field.related_model is None)
                )
            ]


def list_fields_for_ctype(content_type):
    """
    Get a list of (name, verbose_name) tuples of concrete fields from a
    model, via its ContentType.
    """
    if not isinstance(content_type, ContentType):
        raise TypeError("""content_type must be an instance of ContentType.""")
    model = content_type.model_class()
    return list_fields_for_model(model)


def get_usable_model_fields(model):
    """
    Return the list of fields from `model` that meet the criteria: are concrete, aren't
    auto-created, are editable, aren't GenericForeignKeys.

    Parameters
    ----------
    model : model class
            The Model class whose fields we're checking
    """
    return [f.name for f in model._meta.get_fields() if
            f.concrete
            and (
                (not f.auto_created and f.editable)
                or (f.is_relation and f.related_model is None)
                )
            ]


def get_unpermitted_fields(model, user, obj=None):
    """
    Return a list of names of editable fields from `model` the `user` lacks permission for based on
    `obj`.

    Parameters
    ----------
    model : model class
            The Model class whose fields we're checking
    user : User
           The user to check permissions for
    obj : model instance, optional
          The model instance if we're checking change permissions.
    """
    opts = model._meta
    app_label = opts.app_label
    model_name = opts.model_name
    # Work out if we're adding or changing
    if obj is None or not hasattr(obj, 'pk') or obj.pk is None:
        codename = get_permission_codename('add', opts)
    else:
        codename = get_permission_codename('change', opts)

    # If PFPs haven't been created for this model don't look for them.
    if not (hasattr(settings, 'PFP_MODELS')
            and (app_label, model_name) in settings.PFP_MODELS):
        return []

    # If PFP creation for this action has been excluded skip the rest.
    if (hasattr(settings, 'PFP_IGNORE_PERMS')
            and app_label in settings.PFP_IGNORE_PERMS
            and model_name in settings.PFP_IGNORE_PERMS[app_label]
            and codename in settings.PFP_IGNORE_PERMS[app_label][model_name]):
        return []

    # Iterate through fields, return those the user lacks sufficient permissions for
    return [fname for fname in get_usable_model_fields(model) if
            not user.has_perm(
                '{0}.{1}__{2}'.format(app_label, codename, fname),
                obj=obj,
                )
            ]


# def disable_fields(request, model, obj, form, perm=None):
#    """
#    Disable the fields in `form` which the user from `request` doesn't have
#    permission to access. Use `perm` to determine applicable model level
#    permission, or state of `obj` if `perm` is not set.
#    """
#    # Superusers get all the fields
#    if request.user.is_superuser:
#        return form
#
#    # If a permission was passed in use that. Expect a model level
#    # permission. If obj is None assume we're adding, otherwise we're editing
#    c_type = ContentType.objects.get_for_model(model)
#    if perm is None:
#        if obj is None:
#            perm = Permission.objects.get(
#                    content_type=c_type,
#                    codename='add_{}'.format(c_type.model))
#        else:
#            perm = Permission.objects.get(
#                    content_type=c_type,
#                    codename='change_{}'.format(c_type.model))
#
#    # If the user has any PFPS allocated we apply them, otherwise let model
#    # level permissions apply
#    user_query = get_manager_name(Permission, get_user_model())
#    pfps = PerFieldPermission.objects.filter(**{
#            'model_permission': perm,
#            user_query: request.user,
#            }).values_list('field_name', flat=True)
#    if pfps:
#        for fname, field in form.base_fields.items():
#            if fname not in pfps:
#                field.disabled = True
#                field.help_text = ('This field is disabled as you lack required permissions.')
#    return form


# def apply_pfps_to_form(request, form, base_perm, obj=None, disable_fields=True):
#    """
#    Apply PerFieldPermissions to a `ModelForm` to disable/remove fields.
#
#    Parameters
#    ----------
#    request : HttpRequest
#              The request object for this request
#    form : ModelForm
#           The form to apply the permissions to
#    base_perm : Permission
#                The model level permission for the action being performed e.g. add/change
#    obj : Model or None, optional
#          The object if testing object level permissions
#    disable_fields : bool, optional
#                     If True, disable fields on the form, otherwise completely remove them from the
#                     form
#
#    Returns
#    -------
#    ModelForm : ModelForm from parameters with per-field permissions applied.
#    """
#    user = request.user
#    if user.is_superuser:
#        return form
#
#    opts = form.Meta.model._meta
#    model_name = opts.model_name
#
#    # Get fields that are defined on this model (concrete), editable (e.g. not timestamp fields),
#    # and not auto_created (e.g. id), and that the user DOES NOT have permissions for
#    bad_fields = [field.name for field in opts.get_fields() if
#                  (field.concrete and field.editable and not field.auto_created)
#                  and not user.has_perm('{1}.{2}__{3}'.format(model_name,
#                                                              base_perm.codename,
#                                                              field.name),
#                                        obj)
#                  ]
#    if disable_fields:
#        for fname, field in form.base_fields.items():
#            if fname in bad_fields:
#                field.disabled = True
#                field.help_text = ('This field is disabled as you lack required permissions.')
#    else:
#        form = modelform_factory(opts.model, form, exclude=bad_fields)
#
#    return form
