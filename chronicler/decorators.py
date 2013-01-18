''' Decorators for chronicler '''
import functools

from django.utils.decorators import available_attrs

from .models import audit


def audits(model, relations, field_data_key, req_data_key, data_loc=None, force=False):
    ''' Creates an AuditItem with the data provided after a request is
    processed.

    Arguments:
        model: Model that we will be creating an audit entry from
        relations: Relations for the model object we need to track down
        field_data_key: The field on the model we should query against
        req_data_key: The key we should use to get identifying info from
        data_loc: GET, POST, or None. Specifies where we find our data to
        query with.
    '''

    def decorator(view_func):
        @functools.wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if data_loc == 'POST':
                value = request.POST.get(req_data_key)
            elif data_loc == 'GET':
                value = request.GET.get(req_data_key)
            else:
                value = kwargs.get(req_data_key)

            if not value:
                # Couldn't find requested req_data_key in POST/GET
                return view_func(request, *args, **kwargs)

            obj_kwargs = {field_data_key: value}
            obj = model.objects.get(**obj_kwargs)
            response = view_func(request, *args, **kwargs)
            audit.send(
                sender=model,
                instance=obj,
                relations=relations,
                user=request.user,
                force=force
            )
            return response
        return _wrapped_view
    return decorator
