from django import forms
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from perfieldperms.utils import get_unpermitted_fields, list_fields_for_ctype, get_non_pfp_perms


# Forms for permission allocation view
def pfp_perm_select_form_factory(permissions_qs):
    """
    Generate a form with options for permissions that depend on what
    model, permissions, and maybe fields a user has selected in the filters.
    Pass in a queryset of the permissions we want to use.

    Return a formset using this form.
    """
    class PFPSelectForm(forms.Form):
        role_name = forms.CharField(widget=forms.HiddenInput)
        role_id = forms.CharField(widget=forms.HiddenInput)
        permissions = forms.ModelMultipleChoiceField(
                queryset=permissions_qs,
                required=False,
                widget=forms.CheckboxSelectMultiple,
                )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['role_name'].widget.attrs['readonly'] = True
            self.fields['role_id'].widget.attrs['readonly'] = True

    return forms.formset_factory(PFPSelectForm, extra=0, max_num=0)


class PFPRoleFilterForm(forms.Form):
    """
    Form that contains the fields used to filter roles in permission
    management grid.
    """
    prefix = 'pfp_rfilter'
    role_type = forms.ModelChoiceField(queryset=ContentType.objects.none())

    def __init__(self, *args, **kwargs):
        """
        Extend super to set the role_type queryset to allowed ContentTypes."""
        super().__init__(*args, **kwargs)
        user_model = get_user_model()
        roles_qs = ContentType.objects.filter(
                Q(app_label=user_model._meta.app_label, model=user_model.__name__.lower())
                | Q(pfproletype__isnull=False)
                ).distinct()
        self.fields['role_type'].queryset = roles_qs


class PFPPermFilterForm(forms.Form):
    """
    Form that contains the fields used to filter permissions in permission
    management grid.
    """
    prefix = 'pfp_pfilter'
    model = forms.ModelChoiceField(queryset=ContentType.objects.all())
    show_pfps = forms.BooleanField(
            required=False,
            label='field level permissions',
            )
    permissions = forms.ModelMultipleChoiceField(
            queryset=Permission.objects.none(),
            required=False
            )
    model_fields = forms.MultipleChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        """
        Extend super to change the queryset for the model field, and configure
        other fields based on the contents of keyword arg "initial".
        """
        super().__init__(*args, **kwargs)
        models_qs = ContentType.objects.filter(pfpfiltertype__isnull=False)
        if models_qs:
            self.fields['model'].queryset = models_qs

        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'model' in initial:
                model_ctype = initial['model']

                if 'show_pfps' in initial and initial['show_pfps']:
                    permissions_qs = Permission.objects.filter(
                            content_type=model_ctype)
                else:
                    permissions_qs = get_non_pfp_perms(model_ctype)
                self.fields['permissions'].queryset = permissions_qs
                self.fields['model_fields'].choices = list_fields_for_ctype(model_ctype)


# ModelForms for concrete models
class PFPRoleTypesForm(forms.ModelForm):
    """Prevents attempt to duplicate an existing entry by restricting choices."""
    role_ctype = forms.ModelChoiceField(
            queryset=ContentType.objects.filter(
                pfproletype__isnull=True
                ))


class PFPContentTypesForm(forms.ModelForm):
    """Prevents attempt to duplicate an existing entry by restricting choices."""
    content_type = forms.ModelChoiceField(
            queryset=ContentType.objects.filter(
                pfpcontenttype__isnull=True
                ))


# Base ModelForm Classes
class PFPModelForm(forms.ModelForm):
    """
    Extension to ModelForm that modifies fields based on user permissions.

    Attributes
    ----------
    disabled_fields : List, optional
                      A list of field names to disable
    disable_fields : bool, optional
                     If True, disable fields on the form, otherwise completely remove them from the
                     form

    Parameters
    ----------
    disabled_fields : List, optional
                      A list of field names to disable
    disable_fields : bool, optional
                     If True, disable fields on the form, otherwise completely remove them from the
                     form
    user : User, optional
           A user object which will be used to determine which fields to disable on the form.
    """
    disable_fields = True
    disabled_fields = None

    def __init__(self, *args, **kwargs):
        # Overwrite class settings with those passed as kwargs
        if self.disabled_fields is None:
            self.disabled_fields = []
        self.disable_fields = kwargs.pop('disable_fields', self.disable_fields)
        self.disabled_fields = kwargs.pop('disabled_fields', self.disabled_fields)

        # If we were passed a user grab them
        user = None
        if 'user' in kwargs:
            user = kwargs.pop('user')

        super().__init__(*args, **kwargs)

        # If we have a user use them to generate disabled_fields
        if user:
            # If instance.pk is None it's a new unsaved object so 'add' permissions apply,
            # otherwise it's an existing object and we're changing.
            if hasattr(self.instance, 'pk') and self.instance.pk is not None:
                self.disabled_fields = get_unpermitted_fields(
                        self._meta.model,
                        user,
                        obj=self.instance,
                        )
            else:
                self.disabled_fields = get_unpermitted_fields(self._meta.model, user)
        self._filter_fields()

    def _filter_fields(self):
        """Do the field filtering."""
        # Iterate through fields, disabling or removing if the user lacks sufficient permission
        form_fields = list(self.fields)
        for fname in self.disabled_fields:
            if fname in form_fields:
                if self.disable_fields:
                    self.fields[fname].disabled = True
                    self.fields[fname].help_text = ('This field is disabled as you lack required '
                                                    'permissions.')
                else:
                    del self.fields[fname]
