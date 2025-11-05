from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def user_required(view_func):
    """Decorator to ensure only department users can access the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        if not request.user.is_department_user():
            messages.error(request, 'Access denied. This area is for department users only.')
            return redirect('tickets:admin_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to ensure only legal admins can access the view."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login')
        if not request.user.is_legal_admin():
            messages.error(request, 'Access denied. This area is for legal admins only.')
            return redirect('tickets:user_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper




