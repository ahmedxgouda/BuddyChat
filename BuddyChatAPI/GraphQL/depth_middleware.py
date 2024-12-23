from graphql import parse
from django.core.exceptions import ValidationError

class QueryDepthMiddleware:
    def __init__(self, max_depth):
        self.max_depth = max_depth
    
    def resolve(self, next, root, info, **kwargs):
        query = info.operation
        if not query:
            return
        depth = self._get_depth(query)
        if depth > self.max_depth:
            raise ValidationError('Query is too deep, max depth is {}'.format(self.max_depth))
        
        return next(root, info, **kwargs)
        
    def _get_depth(self, node, depth=0):
        if not hasattr(node, 'selection_set') or not node.selection_set:
            return depth
        return max([self._get_depth(selection, depth + 1) for selection in node.selection_set.selections])

depth_middleware = QueryDepthMiddleware(20)
