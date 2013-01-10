from django.conf.urls import *

from voting.views import AjaxJsonVoteView, RedirectVoteView


urlpatterns = patterns('',
    url(r"^vote/direct/(?P<app_label>[\w\.-]+)/(?P<model_name>\w+)/"\
        "(?P<object_id>[^\/]+)/(?P<direction>up|down|clear)/(?:(?P<count>\d+)/)?$",
        RedirectVoteView.as_view(), name="voting-direct"),

    url(r"^vote/(?P<app_label>[\w\.-]+)/(?P<model_name>\w+)/"\
        "(?P<object_id>[^\/]+)/(?P<direction>up|down|clear)/(?:(?P<count>\d+)/)?$",
            AjaxJsonVoteView.as_view(), name="voting"),
)
