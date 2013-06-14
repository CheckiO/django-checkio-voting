from django.db import models
import register


class CalcField(models.IntegerField):
    def __init__(self,*args,**kwargs):
        kwargs['default'] = 0
        self.validate_obj = kwargs.pop('validate_obj',None)
        self.prevalidate_obj = kwargs.pop('prevalidate_obj',None)
        super(CalcField,self).__init__(*args,**kwargs)
    def contribute_to_class(self,cls,name):
        super(CalcField,self).contribute_to_class(cls,name)
        if self.validate_obj:
            register.add_vote_validation(cls, lambda vote: getattr(vote.object, self.validate_obj)(vote))
        if self.prevalidate_obj:
            register.add_vote_prevalidation(cls, lambda vote: getattr(vote.object, self.prevalidate_obj)(vote))
        elif self.validate_obj:
            register.add_vote_prevalidation(cls, lambda vote: getattr(vote.object, self.validate_obj)(vote))


class VotingCountField(CalcField):
    def contribute_to_class(self,cls,name):
        super(VotingCountField,self).contribute_to_class(cls,name)
        register.set_model_count_attribute(cls, name)

class VotingScoreField(CalcField):
    def contribute_to_class(self,cls,name):
        super(VotingScoreField,self).contribute_to_class(cls,name)
        register.set_model_score_attribute(cls, name)

from south.modelsinspector import add_introspection_rules

add_introspection_rules([], ["^voting\.fields\.VotingCountField", "^voting\.fields\.VotingScoreField"])
