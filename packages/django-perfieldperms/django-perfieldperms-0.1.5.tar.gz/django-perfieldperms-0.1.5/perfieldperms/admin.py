from django.contrib import admin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.conf.urls import url
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.db.models import Q
from django.template.response import TemplateResponse
from functools import update_wrapper

from perfieldperms import forms
from perfieldperms import models
from perfieldperms.utils import get_m2m_remote_fields, get_manager_name, get_unpermitted_fields


class PFPModelAdmin(admin.ModelAdmin):
    """
    Extends get_form() to disable/remove fields based on user's field level
    permissions.

    Attributes
    ----------
    pfp_disable_fields : bool
                         Whether to disable fields or remove them from the ModelForm when applying
                         per-field permissions
    """
    pfp_disable_fields = True

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.disabled_fields = get_unpermitted_fields(self.model, request.user, obj)
        form.disable_fields = self.pfp_disable_fields
        return form


class PFPInlineAdmin(admin.options.InlineModelAdmin):
    """
    Extends get_formset() to disable fields based on user's field level
    permissions.

    Attributes
    ----------
    pfp_disable_fields : bool
                         Whether to disable fields or remove them from the ModelForm when applying
                         per-field permissions
    """
    pfp_disable_fields = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        form = formset.form
        form.disabled_fields = get_unpermitted_fields(self.model, request.user, obj)
        form.disable_fields = self.pfp_disable_fields
        return formset


class PerFieldPermissionAdmin(admin.ModelAdmin):
    """
    Extends ModelAdmin by adding a /manage/ url which provides an alternative
    table layout for managing permissions.
    """
    def _get_filter_form_initial(self, request):
        """
        Extracts fields needed to initialise the filter forms from submitted
        data. Uses said forms to verify the submitted data.

        Returns a dict of values needed to initialise the filter forms.
        """
        required_fields = [
                'pfp_pfilter-model', 'pfp_pfilter-show_pfps',
                'pfp_rfilter-role_type',
                ]
        initial = {}
        if request.method == 'GET':
            init_data = self.get_changeform_initial_data(request)
        elif request.method == 'POST':
            init_data = request.POST.copy()
        # Stick the GET or POST data into the form to validate it, and if it
        # validates grab the cleaned data from the required fields which we'll
        # use to populate the non-required fields later on
        init_data = {k: v for k, v in init_data.items() if k in required_fields}
        init_form = forms.PFPPermFilterForm(data=init_data)
        if init_form.is_bound and init_form.is_valid():
            initial['model'] = init_form.cleaned_data['model']
            initial['show_pfps'] = init_form.cleaned_data['show_pfps']

        init_form = forms.PFPRoleFilterForm(data=init_data)
        if init_form.is_bound and init_form.is_valid():
            initial['role_type'] = init_form.cleaned_data['role_type']

        return initial

    def _get_perm_choices(self, cleaned_data):
        """
        Constructs the list of permissions that will be offered to each
        role in the selection matrix. Expects cleaned data from a
        PFPManagePermsForm.

        Returns a Permission queryset.
        """
        model_ctype = cleaned_data['model']
        perms = [perm.id for perm in cleaned_data['permissions']]

        if cleaned_data['model_fields']:
            fields = cleaned_data['model_fields']

            # If fields and permissions have been selected, then for any model
            # level permissions selected get their linked pfps, and include any
            # directly selected pfps. Otherwise, just get pfps for the
            # fields selected.
            if perms:
                model_perms = Permission.objects.filter(
                        perfieldpermission__isnull=True,
                        id__in=perms,
                        ).values_list('id', flat=True)
                pfp_ids = set(perms).difference(set(model_perms))
                perms_qs = Permission.objects.filter(
                        Q(perfieldpermission__field_name__in=fields,
                            perfieldpermission__model_permission_id__in=model_perms)
                        | Q(id__in=pfp_ids)
                        ).distinct().order_by()
            else:
                perms_qs = Permission.objects.filter(
                        content_type=model_ctype,
                        perfieldpermission__field_name__in=fields
                        ).order_by()
        # If fields aren't set then we use the selected permissions, or all
        # available permissions
        elif cleaned_data['permissions']:
            perms_qs = cleaned_data['permissions']
        elif cleaned_data['show_pfps']:
            perms_qs = Permission.objects.filter(
                    content_type=model_ctype).order_by()
        else:
            perms_qs = Permission.objects.filter(
                    content_type=model_ctype,
                    perfieldpermission__isnull=True,
                    ).order_by()
        return perms_qs

    def _get_perm_select_initial(self, request, clean_data, perms_qs):
        """
        Get info about which permissions roles currently possess so we can
        intialise the selection form. Kind of expensive in terms of queries but
        we shouldn't be doing this often.

        Should split this into getting roles, and creating initial tuple.

        Returns a tuple to pass to the formset generated by
        pfp_perm_select_form_factory(), and a Page object for paginating the
        display of the selected roles.
        """
        role_type = clean_data['role_type']
        role_class = role_type.model_class()
        user_model = get_user_model()
        remote_fields = get_m2m_remote_fields(Permission, role_class)
        if len(remote_fields) != 1:
            raise ValidationError('The role type selected has no, or multiple relations to the '
                                  'Permissions model. Expected to find one.')
        else:
            role_related_query = remote_fields[0].name

        initial = []
        all_roles = role_class.objects.all().order_by('pk')

        # Paginate list of roles
        paginator = Paginator(all_roles, 25)
        page = request.GET.get('page')
        try:
            roles = paginator.page(page)
        except PageNotAnInteger:
            roles = paginator.page(1)
        except EmptyPage:
            roles = paginator.page(paginator.num_pages)

        for role in roles:
            perms = perms_qs.filter(**{role_related_query: role}).order_by()
            if role_class == user_model:
                if role.get_full_name():
                    role_name = role.get_full_name()
                else:
                    role_name = role.username
            else:
                role_name = role.name
            initial.append({
                    'role_name': role_name,
                    'role_id': str(role.id),
                    'permissions': perms,
                    })
        return initial, roles

    def _process_perm_forms(self, request, clean_data, perm_formset):
        """
        Add and remove permissions based on form submission.

        Since it's possible users have been added/removed since the list of users was loaded, some
        forms in the formset may have IDs that don't match with what was loaded when the user last
        accessed the form. Skip the user as it would be a pain to try and match them up to an entry
        in the new list of users.
        """
        if perm_formset.forms:
            # perms_offered = perm_formset.forms[0].fields['permissions'].queryset
            role_class = clean_data['role_type'].model_class()
            manager_name = get_manager_name(role_class, Permission)

        for form in perm_formset.forms:
            if form.has_changed() and 'permissions' in form.changed_data:
                if 'role_id' in form.changed_data:
                    messages.warning(
                            request,
                            'Permissions for {} were not updated due to database changes since '
                            'loading the form. Please try again.'.format(
                                form.cleaned_data['role_name']
                                ),
                            )
                    continue

                role_id = form.cleaned_data['role_id']
                selected_perms = set(form.cleaned_data['permissions'])
                try:
                    role = role_class.objects.get(id=role_id)
                except ObjectDoesNotExist:
                    messages.error(
                            request,
                            'Permissions for {} were not updated because the role could not be '
                            'found.'.format(form.cleaned_data['role_name']),
                            )
                    continue

                # Get perms to add/remove
                init_perms = set(form.initial['permissions'])
                del_perms = init_perms.difference(
                        form.cleaned_data['permissions'])
                add_perms = selected_perms.difference(init_perms)

                # Process
                perm_manager = getattr(role, manager_name)
                with transaction.atomic():
                    perm_manager.remove(*del_perms)
                    perm_manager.add(*add_perms)

                messages.success(
                        request,
                        'Permissions for {} were changed. Added: {}. Removed: {}.'.format(
                            form.cleaned_data['role_name'],
                            len(add_perms),
                            len(del_perms),
                            )
                        )

    def manage_view(self, request):
        """
        Provide a filterable grid of roles/permissions as an alternative to
        editing each user/role individually.
        """
        if not(request.user.has_perm('perfieldperms.manage_permissions')):
            raise PermissionDenied

        context = {}
        template = '{}/perfieldperm_manage.html'.format(
                self.model._meta.app_label)
        page = None
        initial = self._get_filter_form_initial(request)
        data = request.POST
        perm_filter_form = forms.PFPPermFilterForm(initial=initial, data=data)
        role_filter_form = forms.PFPRoleFilterForm(initial=initial, data=data)

        if ((role_filter_form.is_bound and role_filter_form.is_valid())
                and
                (perm_filter_form.is_bound and perm_filter_form.is_valid())):
            # Filter forms are valid so see if we have a valid selection form
            clean_data = perm_filter_form.cleaned_data.copy()
            clean_data.update(role_filter_form.cleaned_data)
            perms_qs = self._get_perm_choices(clean_data)
            PermSelectFormSet = forms.pfp_perm_select_form_factory(perms_qs)
            # Generate initial data for formset which will be a list of roles
            # and any permissions they currently have.
            perm_select_initial, page = self._get_perm_select_initial(
                    request,
                    clean_data,
                    perms_qs,
                    )

            if '_save' in request.POST or '_continue' in request.POST:
                perm_formset = PermSelectFormSet(
                        initial=perm_select_initial,
                        data=data,
                        )
                try:
                    if perm_formset.is_bound and perm_formset.is_valid():
                        self._process_perm_forms(request, clean_data, perm_formset)
                except ValidationError:
                    messages.error(request, 'The form failed to validate, probably due to changes '
                                            'to filter settings.')
            else:
                perm_formset = PermSelectFormSet(initial=perm_select_initial)
            context['perm_formset'] = perm_formset

        # Update context with info required by the AdminSite, and the template
        context.update(self.admin_site.each_context(request))
        context.update(dict(
                opts=self.model._meta,
                title='Manage permissions',
                save_as=self.save_as,
                save_as_continue=self.save_as_continue,
                show_save=True,
                show_save_and_continue=True,
                show_save_and_add_another=False,
                show_save_as_new=False,
                perm_filter_form=perm_filter_form,
                role_filter_form=role_filter_form,
                page=page,
                ))
        return TemplateResponse(request, template, context=context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urls = [
                url(r'^manage/$', wrap(self.manage_view),
                    name='{0[0]}_{0[1]}_manage'.format(info)),
                ]
        return urls + super().get_urls()


admin.site.register(models.PerFieldPermission, PerFieldPermissionAdmin)


@admin.register(models.PFPContentType)
class PFPContentTypeAdmin(admin.ModelAdmin):
    form = forms.PFPContentTypesForm


@admin.register(models.PFPRoleType)
class PFPRoleTypeAdmin(admin.ModelAdmin):
    form = forms.PFPRoleTypesForm
