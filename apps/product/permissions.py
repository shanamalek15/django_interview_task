from django.core.exceptions import PermissionDenied
from functools import wraps
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import *


def can_update_delete_category_view(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        obj = get_object_or_404(Category, pk=kwargs["pk"])
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



def can_update_delete_view_product(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
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
        obj = get_object_or_404(Product, pk=kwargs["pk"])
        if request.user.role == 'admin':
            return view(request, *args, **kwargs)
        elif request.user.role == 'staff':
            if obj.created_by == request.user or obj.created_by.role == 'agent':
                return view(request, *args, **kwargs)
        raise PermissionDenied
    return _view

