__all__ = ['set_model_count_attribute', 'set_model_score_attribute', 'add_vote_validation', 'validate_vote']

from django.db import models
from signals import post_vote
from voting.models import Vote
from django.contrib.contenttypes.models import ContentType

MODEL_COUNT_ATTRIBUTES = {}
MODEL_SCORE_ATTRIBUTES = {}
VALIDATIONS = {}
RANGES = {}

def recalc_model_count_attribute(vote, **kwargs):
    obj = vote.object
    attribute_name = MODEL_COUNT_ATTRIBUTES[(obj._meta.app_label, obj._meta.module_name)]
    setattr(obj, attribute_name, Vote.objects.filter_object(obj).count())
    obj.save()

def set_model_count_attribute(model, name):
    if isinstance(model, tuple):
        _key = model
        _sender = ContentType.objects.get(app_label=model[0], model=model[1]).model_class()
    else:
        _sender = model
        _key = (model._meta.app_label, model._meta.module_name)

    MODEL_COUNT_ATTRIBUTES[_key] = name
    post_vote.connect(recalc_model_count_attribute, sender=_sender)


def recalc_model_score_attribute(vote, **kwargs):
    obj = vote.object
    attribute_name = MODEL_SCORE_ATTRIBUTES[(obj._meta.app_label, obj._meta.module_name)]
    setattr(obj, attribute_name, Vote.objects.get_score(obj)['score'])
    obj.save()

def set_model_score_attribute(model, name):
    if isinstance(model, tuple):
        _key = model
        _sender = ContentType.objects.get(app_label=model[0], model=model[1]).model_class()
    else:
        _sender = model
        _key = (model._meta.app_label, model._meta.module_name)
    MODEL_SCORE_ATTRIBUTES[_key] = name
    post_vote.connect(recalc_model_score_attribute, sender=_sender)

def add_vote_validation(model, validation):
    if not isinstance(model, tuple):
        model = (model._meta.app_label, model._meta.module_name)
    VALIDATIONS.setdefault(model,[]).append(validation)

def validate_vote(vote):
    model =  (vote.object._meta.app_label, vote.object._meta.module_name)
    if model not in VALIDATIONS:
        return

    for validation in VALIDATIONS[model]:
        validation(vote)

def add_votes_range(model, range):
    if not isinstance(model,  tuple):
        model = (model._meta.app_label, model._meta.module_name)
    RANGES.setdefault(model,[]).append(range)

def votes_range(obj, user):
    import voting.settings as S
    model = (obj._meta.app_label, obj._meta.module_name)
    if model not in RANGES:
        return range(S.MIN_VOTE_COUNT, S.MAX_VOTE_COUNT+1)
    _range = set(RANGES[model][0](obj, user))
    for r in RANGES[model][1:]:
        _range &= set(r(obj, user))
    return sorted(list(_range))
