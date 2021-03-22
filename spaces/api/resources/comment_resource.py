from import_export import resources
from api.models.comment import Comment

class CommentResource(resources.ModelResource):
    class Meta:
        model = Comment
