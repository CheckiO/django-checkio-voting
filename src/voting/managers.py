from django.contrib.contenttypes.models import ContentType
from django.db import models


class VoteManager(models.Manager):

    def filter_object(self,obj):
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(object_id=obj._get_pk_val(),
            content_type=ctype)

    def get_score(self, obj):
        """
        Get a dictionary containing the total score for ``obj`` and
        the number of votes it's received.
        """

        ret =  self.filter_object(obj).aggregate(num_votes=models.Count('user'), score=models.Sum('vote'))
        ret['score'] = ret['score'] or 0 #this shit is because score = None then object doesn't have a votes at all
        return ret


    def record_vote(self, obj, user, vote):
        """
        Record a user's vote on a given object. Only allows a given user
        to vote once, though that vote may be changed.

        A zero vote indicates that any existing vote should be removed.
        """
        assert  user.is_authenticated()
        import settings as S
        import register

        try:
            v = self.filter_object(obj).get(user=user)
            if v.vote == vote:
                return v
            v.prev_vote = v.vote
            v.vote = vote
        except models.ObjectDoesNotExist:
            ctype = ContentType.objects.get_for_model(obj)
            v = self.model(user=user, content_type=ctype,
                object_id=obj._get_pk_val(), vote=vote)

        S.LAMBDA_VALID_VOTE(v)
        register.validate_vote(v)
        v.save()
        return v
            



    def get_for_user(self, obj, user):
        """
        Get the vote made on the given object by the given user, or
        ``None`` if no matching vote exists.
        """
        assert  user.is_authenticated()

        try:
            vote = self.filter_object(obj).get(user=user)
        except models.ObjectDoesNotExist:
            vote = None
        return vote
