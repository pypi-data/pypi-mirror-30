from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.core.exceptions import ObjectDoesNotExist

from perfieldperms.models import PerFieldPermission


class PFPBackend(object):
    """
    Provide permission checking hooks for PerFieldPermissions.
    """
    mbackend = ModelBackend()

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Use the Django default backend for authentication."""
        return self.mbackend.authenticate(request, username=username, password=password, **kwargs)

    def _cache_to_set(self, cache):
        """Flatten a cache dict of sets into a single set."""
        perms = set()
        perms.update(cache.keys())
        perms.update(*cache.values())
        return perms

    def _merge_caches(self, to_cache, from_cache):
        """
        Merge the entries from one cache into another. In this case an empty
        set overwrites a non-empty set.
        """
        for key, value in from_cache.items():
            if key in to_cache and value:
                to_cache[key].update(value)
            else:
                # to_cache has no entry for this key, or we're overwriting with
                # an empty set
                to_cache[key] = value
        return to_cache

    def _create_perm_sets(self, perms):
        """
        With the perms iterable of (app_label, codename) tuples, create a dict
        of sets to support looking up field level permissions. Return the new dict.
        """
        perm_sets = dict()
        for perm in ['{}.{}'.format(ct, name) for ct, name in perms]:
            perm_sets[perm] = set()
        return perm_sets

    def _update_perm_sets(self, pfps, perm_sets=None):
        """
        With the pfps iterable of (app_label, codename, model_codename) tuples,
        update the appropriate set in the perm_sets dict with the field level
        perms. Return the new dict.
        """
        # Should test if perm_sets != None and pfps=False to avoid accidental
        # overwrites of cache structure
        if perm_sets is None:
            perm_sets = dict()

        for perm, key in [
                ('{}.{}'.format(ct, name), '{}.{}'.format(ct, model_name))
                for ct, name, model_name in pfps]:
            if key in perm_sets:
                perm_sets[key].add(perm)
            else:
                perm_sets[key] = set([perm])
        return perm_sets

    def _get_user_permissions(self, user_obj):
        # Get standard perms
        perms = user_obj.user_permissions.filter(
                perfieldpermission__isnull=True,
                ).values_list('content_type__app_label', 'codename')
        perm_sets = self._create_perm_sets(perms)
        # Get per field perms
        pfps = PerFieldPermission.objects.filter(
                user=user_obj
                ).values_list(
                'content_type__app_label',
                'codename',
                'model_permission__codename',
                )
        perm_sets = self._update_perm_sets(pfps, perm_sets)
        return perm_sets

    def _get_group_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field('groups')
        user_groups_query = 'group__{}'.format(
                user_groups_field.related_query_name()
                )
        perms = Permission.objects.filter(**{
                'perfieldpermission__isnull': True,
                user_groups_query: user_obj
                }).values_list('content_type__app_label', 'codename')
        perm_sets = self._create_perm_sets(perms)
        pfps = PerFieldPermission.objects.filter(
                **{user_groups_query: user_obj}
                ).values_list(
                'content_type__app_label',
                'codename',
                'model_permission__codename',
                )
        perm_sets = self._update_perm_sets(pfps, perm_sets)
        return perm_sets

    def _get_permissions(self, user_obj, obj, from_name):
        """
        Lookup group or user permissions for `user_obj` depending on the
        contents of `from_name`. `from_name` can ber "user" or "group", and
        calls `_get_user_permissions` and `_get_group_permissions`
        respectively.
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        cache_name = '_pfp_{}_perm_cache'.format(from_name)
        if not hasattr(user_obj, cache_name):
            if user_obj.is_superuser:
                perms = Permission.objects.filter(
                        perfieldpermission__isnull=True,
                        ).values_list('content_type__app_label', 'codename')
                perm_sets = self._create_perm_sets(perms)
            else:
                perm_sets = getattr(self, '_get_{}_permissions'.format(from_name))(user_obj)
            setattr(user_obj, cache_name, perm_sets)
        return self._cache_to_set(getattr(user_obj, cache_name))

    def get_user_permissions(self, user_obj, obj=None):
        """Get permissions granted only to this user."""
        return self._get_permissions(user_obj, obj, 'user')

    def get_group_permissions(self, user_obj, obj=None):
        """Get permissions granted to groups this user is a member of."""
        return self._get_permissions(user_obj, obj, 'group')

    def get_all_permissions(self, user_obj, obj=None):
        """
        Get all user and role based permissions for this user. Creates a cache of permissions for
        life of user object.
        """
        if not user_obj.is_active or user_obj.is_anonymous:
            return set()

        if not hasattr(user_obj, '_pfp_perm_cache'):
            self.get_user_permissions(user_obj, obj)
            self.get_group_permissions(user_obj, obj)
            # Copy the group perm cache, then update it from the user cache
            # effectively overriding those settings
            user_obj._pfp_perm_cache = user_obj._pfp_group_perm_cache.copy()
            user_obj._pfp_perm_cache.update(user_obj._pfp_user_perm_cache)
            # The below will merge caches instead of overwriting
            # user_obj._pfp_perm_cache = self._merge_caches(
            #        user_obj._pfp_perm_cache,
            #        user_obj._pfp_user_perm_cache,
            #        )
        return self._cache_to_set(user_obj._pfp_perm_cache)

    def has_perm(self, user_obj, perm, obj=None):
        """
        Returns true if `user_obj` has `perm` in their set of all permissions.
        """
        if not user_obj.is_active:
            return False
        if not hasattr(user_obj, '_pfp_perm_cache'):
            if not self.get_all_permissions(user_obj, obj):
                return False
        cache = user_obj._pfp_perm_cache
        # Looking for model level perm, no need to go deeper
        if perm in cache:
            return True
        perm_split = perm.rsplit('__', maxsplit=1)
        perm_key = perm_split[0]
        # A user has a field level permission if the model level parent is set
        # and no fields are set, or the field permission is set.
        return perm_key in cache and (
                not cache[perm_key] or perm in cache[perm_key]
                )

    def has_module_perms(self, user_obj, app_label):
        """
        Returns True if `user_obj` has any permissions in the given
        `app_label`.
        """
        if not user_obj.is_active:
            return False
        if not hasattr(user_obj, '_pfp_perm_cache'):
            if not self.get_all_permissions(user_obj):
                return False
        for perm in user_obj._pfp_perm_cache.keys():
            if perm[:perm.index('.')] == app_label:
                return True
        return False

    def has_all_fields(self, user_obj, perm, obj=None):
        """
        Return if `user_obj` has all field level permissions for a given
        permission, in which case the set of field permissions will be empty
        """
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return False

        if isinstance(perm, type(str())):
            app_label, codename = perm.split('.')
            try:
                perm = PerFieldPermission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                    )
            except ObjectDoesNotExist:
                perm = Permission.objects.get(
                    content_type__app_label=app_label,
                    codename=codename,
                    )
        if isinstance(perm, PerFieldPermission):
            perm_key = '{}.{}'.format(
                    perm.content_type.app_label,
                    perm.model_permission.codename,
                    )
        elif isinstance(perm, Permission):
            perm_key = '{}.{}'.format(perm.content_type.app_label, perm.codename)
        else:
            raise TypeError("""Perm must be a string representation of a
            Permission, a Permission, or a PerFieldPermission""")

        if not hasattr(user_obj, '_pfp_perm_cache'):
            self.get_all_permissions(user_obj, obj)
        cache = user_obj._pfp_perm_cache
        return perm_key in cache and not cache[perm_key]

    def get_user(self, user_id):
        return self.mbackend.get_user(user_id)
