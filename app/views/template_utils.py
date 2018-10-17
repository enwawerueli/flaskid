from . import main_blueprint


@main_blueprint.add_app_template_filter
def date(date):
    return date.strftime('%A %B %d %Y')


@main_blueprint.add_app_template_filter
def month(date):
    return date.strftime('%B')


@main_blueprint.add_app_template_filter
def count(collection):
    return len(collection)
