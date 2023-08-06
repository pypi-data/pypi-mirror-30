Implements permissions for model fields in Django

Requirements
============
* Python 3.4+
* Django 1.11+ 

Installation
============
Include the 'perfieldperms' directory in your Django project as an application.
OR
Use pip to install it as a package.

Add ``perfieldperms.apps.PerfieldpermsConfig`` to Django's installed
applications.

Add ``perfieldperms.backends.PFPBackend`` to ``AUTHENTICATION_BACKENDS`` in
your ``settings.py``

Run ``manage.py migrate``

Configuration
=============
perfieldperms is configurable via ``settings.py`` or via internal models.

settings.py
-----------
PFP_MODELS -- an iterable of two tuples [(app_label, model name)] of models you
want perfieldpermissions (pfps) created for.

PFP_IGNORE_PERMS -- a dict of dicts of iterables of permissions you want
ignored when creating pfps. Structured::
    {app_label:
        {model name: [<perm codename>, <perm codename>,..]}
    }

PFP_IGNORE_DELETE -- By default perfieldperms doesn't create field level delete
permissions as this doesn't necessarily make sense. Set to False if you want to
create delete pfps.

Internal models
---------------
PFPContentType -- Django ContentTypes you want to create pfps. This setting is
merged with PFP_MODELS from ``settings.py``.

Use
===
After configuring which models you want to creats pfps for run the management
command ``pfp-makeperms``.

PerFieldPermission subclasses Permission so pfps can be accessed, allocated and
tested as normal Permission objects. PerFieldPermissions are linked to a parent
"model permission" to create the appropriate hierarchy. Depending on needs you
may not need to access the actual PerFieldPermission objects.

Perfieldperms tries to take a Principle of Least Astonishment approach to
testing permissions, while attempting to support reasonably complicated
permission structures:
* If a user has a model level permission but no field permissions, they
  are deemed to have all equivalent field permissions (all field permissions
  linked to that model permission).
* Model permissions remain additive as in out of the box Django.
* Field permissions allocated to groups are additive, so field permissions for
  all a user's groups are merged.
* Field permissions allocated to a user override those allocated to groups they
  are a member of. The effect is to explicitly set the fields the user has
  access to. This allows for the creation of limited exceptions within groups.
* Possession of a field permission implies access to the model, so testing
  access to a model via e.g. ModelAdmin had_add_permission() will succeed if
  the user has any applicable field permission.

Admin interface
---------------
Two ModelAdmins ``PFPModelAdmin`` and ``PFPInlineAdmin`` are provided that
extend the appropriate ModelAdmin, disabling fields in forms as appropriate.
These can be used as is or as Mixins to extend other ModelAdmin classes.

There is a permissions management view accessible under
*/admin/perfieldperms/perfieldpermission/manage/*. It provides an alternative
interface to allocating permissions based on a set of filters for
permissions/roles (where a role is a user or group,) and generates a table
based form listing permissions against users. It is terrible and needs
replacing :)

Tests
=====
Use ``runtests.py`` to run tests. Test sub-modules and individual tests can be
targetted by supplying the appropriate python module address as an argument to
the script.
