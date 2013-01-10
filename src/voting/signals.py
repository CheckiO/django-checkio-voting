__all__ = ['post_vote', 'pre_vote']

from django.dispatch import Signal
from django.db.models.signals import pre_save, post_save
from voting.models import Vote

#vote gets addition attribute prev_vote to know previous state
#by default it's zero

pre_vote = Signal(providing_args=['vote'])
post_vote = Signal(providing_args=['vote'])

def pre_vote_send(instance, raw, **kwargs):
    if raw:
        return
    pre_vote.send(sender=instance.object.__class__, vote=instance)
pre_save.connect(pre_vote_send, sender=Vote)

def post_vote_send(instance, raw, **kwargs):
    if raw:
        return
    post_vote.send(sender=instance.object.__class__, vote=instance)
post_save.connect(post_vote_send, sender=Vote)
