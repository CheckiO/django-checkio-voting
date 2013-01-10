
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import get_model
from django.http import  HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.contrib import messages
from voting.exceptions import VoteValidationError

from voting.models import Vote
import voting.settings as S
from django.views.generic import View

from django.core.serializers.json import DjangoJSONEncoder



VOTE_DIRECTIONS = {
    'up': 1,
    'down': -1,
    'clear': 0
}

class BaseVoteView(View):
    '''
        Base class fot voting views
    '''

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated():
            return self.response_anonymous()

        try:
            vote = VOTE_DIRECTIONS[self.kwargs['direction']]
        except KeyError:
            return self.response_error('Wrong request. Direction.')

        if self.kwargs.get('count'):
            vote *= int(self.kwargs['count'])

        model = get_model(self.kwargs['app_label'], self.kwargs['model_name'])
        if not model:
            return self.response_error('Wrong request. Model.')

        try:
            obj = model._default_manager.get(**{
                '%s__exact' % model._meta.pk.name : self.kwargs['object_id']
            })
        except ObjectDoesNotExist:
            return self.response_error('Wrong request. Object.')

        try:
            vote = Vote.objects.record_vote(obj, self.request.user, vote)
        except VoteValidationError, e:
            return self.response_error(e.error_message)

        return self.success_vote(vote)

    def response_error(self, error_message):
        raise NotImplementedError

    def response_anonymous(self):
        raise NotImplementedError

    def success_vote(self, vote):
        raise NotImplementedError




class AjaxJsonVoteView(BaseVoteView):
    """
     for use via XMLHttpRequest.

    Properties of the resulting JSON object:
        success
            ``true`` if the vote was successfully processed, ``false``
            otherwise.
        score
            The object's updated score and number of votes if the vote
            was successfully processed.
        error_message
            Contains an error message if the vote was not successfully
            processed.
    """

    def response_json(self,data):
        return HttpResponse(simplejson.dumps(data, cls=DjangoJSONEncoder),
            mimetype='application/json')

    def response_error(self, error_message):
        return self.response_json({
            'success': False,
            'error_message': error_message
        })

    def response_anonymous(self):
        return self.response_error('Anonymous user can not vote')

    def success_vote(self,vote):
        return self.response_json({
            'success': True,
            'score': Vote.objects.get_score(vote.object),
        })

class RedirectVoteView(BaseVoteView):
    """
        using redirects and django.contrib.messages
    """
    def get_next_url(self):
        request = self.request
        return request.GET.get('next', request.META.get('HTTP_REFERER') or S.REDIRECT_VIEW_DEFAULT_URL)


    def response_error(self, error_message):
        messages.error(self.request, error_message)
        return HttpResponseRedirect(self.get_next_url())

    def response_anonymous(self):
        return redirect_to_login(self.get_next_url())

    def success_vote(self, vote):
        messages.info(self.request, S.REDIRECT_VIEW_THANKS_MESSAGE.format(vote=vote))
        return HttpResponseRedirect(self.get_next_url())

