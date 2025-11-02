from functools import wraps
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def ban_guard(view):
    """Блокирует доступ забаненным пользователям"""
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        u = request.user
        if u.is_authenticated and getattr(u, 'is_banned', False):
            return HttpResponseForbidden('Ваш аккаунт заблокирован.')
        return view(request, *args, **kwargs)
    return _wrapped
