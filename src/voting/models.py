from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models

from voting.managers import VoteManager



class Vote(models.Model):
    """
    A vote on an object by a User.
    """
    user         = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id    = models.PositiveIntegerField()
    object       = generic.GenericForeignKey('content_type', 'object_id')
    vote         = models.SmallIntegerField()

    prev_vote = 0 # to know about changing in post_vote and pre_vote signals

    objects = VoteManager()
    
    @property
    def cls_name(self):
        content_type = self.content_type
        return '.'.join((content_type.app_label, content_type.model))

    @property
    def vote_text(self):
        return '+'+str(self.vote) if self.vote>0 else str(self.vote)
    class Meta:
        db_table = 'votes'
        # One vote per user per object
        unique_together = (('user', 'content_type', 'object_id'),)

    def __unicode__(self):
        return u'%s: %s on %s' % (self.user, self.vote, self.object)
