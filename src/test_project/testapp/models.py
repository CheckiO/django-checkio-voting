from django.contrib.auth.models import User
from django.db import models
from voting.exceptions import VoteValidationError
from voting.fields import VotingScoreField, VotingCountField

class Comment(models.Model):
    author = models.ForeignKey('auth.user')
    text = models.TextField()

class Article(models.Model):
    author = models.ForeignKey('auth.user')
    subject = models.CharField(max_length=100)


class Book(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    total_voting_score = VotingScoreField()


class Shelf(models.Model):
    num=models.IntegerField(default=1)
    tvs = VotingScoreField()
    tvc = VotingCountField()

class StrictlyComment(models.Model):
    author = models.ForeignKey('auth.user')
    text = models.TextField()
    tvs = VotingScoreField(validate_obj='voting_validate', range_obj='votes_range')

    def voting_validate(self, vote):
        if vote.object.author == vote.user:
            raise VoteValidationError, "Author can't for his comment"

    def votes_range(self, user):
        return [-1,0,1]

from voting import register

def validate_user_vote(vote):
    if vote.object == vote.user:
        raise VoteValidationError, "You can't vote for yourself"

register.add_vote_validation(User, validate_user_vote)
