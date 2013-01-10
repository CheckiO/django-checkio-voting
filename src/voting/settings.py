# -*- coding: utf-8 -*-

from django.conf import settings


#VOTING_MAX_VOTE_COUNT and VOTING_MIN_VOTE_COUNT of possible vote count for default vote validation
MAX_VOTE_COUNT = getattr(settings, 'VOTING_MAX_VOTE_COUNT', 1)
MIN_VOTE_COUNT = getattr(settings, 'VOTING_MIN_VOTE_COUNT', -1)

from exceptions import VoteValidationError
def default_valid_vote(vote):
    if vote.vote > MAX_VOTE_COUNT:
        raise VoteValidationError, 'Wrong request. Vote is too high.'
    if vote.vote < MIN_VOTE_COUNT:
        raise VoteValidationError, 'Wrong request. Vote is too low.'


# function for validation created or updated vote before it will save.
LAMBDA_VALID_VOTE = getattr(settings, 'VOTING_LAMBDA_VALID_VOTE', default_valid_vote )

# message that will be shown user after vote in redirect message
# user gets this message after formatting with vote object,
# so this settings can looks like this "Thank you for your vote for {vote.object}"
REDIRECT_VIEW_THANKS_MESSAGE = getattr(settings, 'VOTING_REDIRECT_VIEW_THANKS_MESSAGE', 'Thank you for your vote')

# where to redirect in case GET['next'] and META['HTTP_REFERER'] didn't passed
REDIRECT_VIEW_DEFAULT_URL = getattr(settings, 'VOTING_REDIRECT_VIEW_DEFAULT_URL', '/')