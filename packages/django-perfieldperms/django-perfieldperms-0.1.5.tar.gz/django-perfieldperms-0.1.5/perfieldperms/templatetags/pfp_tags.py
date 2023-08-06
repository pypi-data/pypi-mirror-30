from django import template

register = template.Library()


@register.inclusion_tag('perfieldperms/pfp_submit_line.html', takes_context=True)
def pfp_submit_row(context):
    ctx = context.update(dict(
            show_save=True,
            show_delete_link=False,
            show_save_as_new=False,
            show_save_and_add_another=False,
            show_save_and_continue=True,
            ))
    return ctx


@register.inclusion_tag('perfieldperms/pfp_filter_field.html')
def pfp_filter_field(field):
    ctx = {'field': field}
    return ctx
