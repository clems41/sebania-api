from sebania.utils import db_utils


def get_ferme_from_context(context):
    if "ferme" not in context:
        request = context.get("request")
        ferme = db_utils.get_ferme_from_request(request)
        context.update({"ferme": ferme})
    return context.get("ferme")