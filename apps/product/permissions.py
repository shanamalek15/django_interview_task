from django.core.exceptions import PermissionDenied
from functools import wraps
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings

def agent_restriction(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)  
        if request.user.role == 'agent':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def can_update_delete_category_view(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)  
        obj = get_object_or_404(Category, pk=kwargs["pk"])
        user_role = request.user.role
        if user_role == 'admin':
            return view(request, *args, **kwargs)
        elif user_role == 'staff':
            if obj.created_by == request.user or obj.created_by.role == 'agent':
                return view(request, *args, **kwargs)    
        raise PermissionDenied
    return _view


def can_update_delete_view_product(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)  
        obj = get_object_or_404(Product, pk=kwargs["pk"])
        user_role = request.user.role
        
        if user_role == 'admin':
            return view(request, *args, **kwargs)
        elif user_role == 'staff':
            if obj.created_by == request.user or obj.created_by.role == 'agent':
                return view(request, *args, **kwargs)
        elif user_role == 'agent':
            if obj.created_by == request.user:
                return view(request, *args, **kwargs)
        
        raise PermissionDenied
    return _view


def can_give_approval_product(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)  
        obj = get_object_or_404(Product, pk=kwargs["pk"])
        if request.user.role == 'admin':
            return view(request, *args, **kwargs)
        elif request.user.role == 'staff':
            if obj.created_by == request.user or obj.created_by.role == 'agent':
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return _view

