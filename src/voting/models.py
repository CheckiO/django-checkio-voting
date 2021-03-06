from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models

from voting.managers import VoteManager
from voting.exceptions import VoteValidationError


class Vote(models.Model):
    """
    A vote on an object by a User.
    """
    user         = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id    = models.PositiveIntegerField()
    object       = generic.GenericForeignKey('content_type', 'object_id')
    vote         = models.SmallIntegerField()
    added_at     = models.DateTimeField(auto_now=True, null=True)

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

    def save(self, *args, **kwargs):
        if self.pk:
            prev = Vote.objects.get(pk=self.pk)
            self.prev_vote = prev.vote
        change_vote = self.vote - self.prev_vote
        if change_vote:
            voting.signals.change_vote.send(sender=self.object, vote=self)
        super(Vote, self).save(*args, **kwargs)

    def is_upvote(self):
        return self.vote > 0

    def is_downvote(self):
        return self.vote < 0

    @classmethod
    def get_votes_range(cls, obj, user):
        """
        Get votes range for the given object by the given user.
        """
        import voting.register as R
        return R.votes_range(obj, user)

import voting.signals
