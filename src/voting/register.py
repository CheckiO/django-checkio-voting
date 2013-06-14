__all__ = ['set_model_count_attribute', 'set_model_score_attribute', 'add_vote_validation', 'validate_vote']

from signals import post_vote
from voting.models import Vote

MODEL_COUNT_ATTRIBUTES = {}
MODEL_SCORE_ATTRIBUTES = {}
VALIDATIONS = {}
PREVALIDATIONS = {}

def recalc_model_count_attribute(vote, **kwargs):
    obj = vote.object
    attribute_name = MODEL_COUNT_ATTRIBUTES[obj.__class__]
    setattr(obj, attribute_name, Vote.objects.filter_object(obj).count())
    obj.save()

def set_model_count_attribute(model, name):
    MODEL_COUNT_ATTRIBUTES[model] = name
    post_vote.connect(recalc_model_count_attribute, sender=model)


def recalc_model_score_attribute(vote, **kwargs):
    obj = vote.object
    attribute_name = MODEL_SCORE_ATTRIBUTES[obj.__class__]
    setattr(obj, attribute_name, Vote.objects.get_score(obj)['score'])
    obj.save()

def set_model_score_attribute(model, name):
    MODEL_SCORE_ATTRIBUTES[model] = name
    post_vote.connect(recalc_model_score_attribute, sender=model)

def add_vote_validation(model, validation):
    VALIDATIONS.setdefault(model,[]).append(validation)

def validate_vote(vote):
    model = vote.object.__class__
    if model not in VALIDATIONS:
        return

    for validation in VALIDATIONS[model]:
        validation(vote)

def add_vote_prevalidation(model, prevalidation):
    PREVALIDATIONS.setdefault(model,[]).append(prevalidation)

def prevalidate_vote(vote):
    model = vote.object.__class__
    if model not in PREVALIDATIONS:
        return

    for prevalidation in PREVALIDATIONS[model]:
        prevalidation(vote)
