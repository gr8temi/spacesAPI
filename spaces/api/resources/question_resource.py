from import_export import resources
from api.models.question import Question

class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question
