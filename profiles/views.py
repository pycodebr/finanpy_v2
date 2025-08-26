"""
Profile views for user profile management in the Finanpy financial system.

This module implements class-based views for profile functionality with:
- User data isolation and security
- Profile creation and editing capabilities
- Integration with Django's authentication system
- Responsive templates with TailwindCSS styling
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import DetailView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.http import Http404
from typing import Any, Dict

from .models import Profile
from .forms import ProfileForm


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Display user profile information with read-only view.
    
    This view shows comprehensive profile information for the authenticated user
    with proper data isolation. Only the profile owner can view their profile.
    """
    model = Profile
    template_name = 'profiles/profile_detail.html'
    context_object_name = 'profile'
    
    def get_object(self, queryset=None):
        """
        Get the profile for the current authenticated user.
        Creates profile if it doesn't exist.
        """
        try:
            # Try to get existing profile
            profile = Profile.objects.get(user=self.request.user)
            return profile
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=self.request.user)
            messages.info(
                self.request, 
                'Perfil criado automaticamente. Complete suas informações pessoais.'
            )
            return profile
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add additional context data for the template.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = self.get_object()
        
        # Calculate profile completion percentage
        completion_fields = [
            profile.first_name,
            profile.last_name,
            profile.phone,
            profile.birth_date,
            profile.bio
        ]
        completed_fields = sum(1 for field in completion_fields if field)
        completion_percentage = int((completed_fields / len(completion_fields)) * 100)
        
        # Add context data
        context.update({
            'user': user,
            'completion_percentage': completion_percentage,
            'completed_fields': completed_fields,
            'total_fields': len(completion_fields),
            'profile_age': profile.age,
            'can_edit': True,  # User can always edit their own profile
        })
        
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Update user profile information with form validation.
    
    This view allows authenticated users to edit their profile information
    with proper validation and user feedback. Only the profile owner can
    edit their profile.
    """
    model = Profile
    form_class = ProfileForm
    template_name = 'profiles/profile_edit.html'
    success_message = 'Perfil atualizado com sucesso!'
    context_object_name = 'profile'
    
    def get_object(self, queryset=None):
        """
        Get the profile for the current authenticated user.
        Creates profile if it doesn't exist.
        """
        try:
            # Try to get existing profile
            profile = Profile.objects.get(user=self.request.user)
            return profile
        except Profile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = Profile.objects.create(user=self.request.user)
            messages.info(
                self.request,
                'Novo perfil criado. Preencha suas informações pessoais.'
            )
            return profile
    
    def get_success_url(self):
        """
        Redirect to profile detail view after successful update.
        """
        return reverse_lazy('profiles:detail')
    
    def form_valid(self, form):
        """
        Handle successful form submission with proper data validation.
        """
        try:
            with transaction.atomic():
                # Ensure the profile belongs to the current user
                profile = form.save(commit=False)
                profile.user = self.request.user
                profile.save()
                
                # Add success message with personalization
                user_name = profile.get_short_name()
                messages.success(
                    self.request,
                    f'Perfeito, {user_name}! Seu perfil foi atualizado com sucesso.'
                )
                
                return super().form_valid(form)
                
        except ValidationError as e:
            # Handle model validation errors
            messages.error(
                self.request,
                f'Erro de validação: {str(e)}'
            )
            return self.form_invalid(form)
        except Exception as e:
            # Handle unexpected errors
            messages.error(
                self.request,
                'Ocorreu um erro ao salvar o perfil. Tente novamente.'
            )
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """
        Handle form validation errors with user-friendly messages.
        """
        # Count the number of errors
        error_count = sum(len(errors) for errors in form.errors.values())
        
        if error_count == 1:
            messages.error(
                self.request,
                'Por favor, corrija o erro indicado no formulário.'
            )
        else:
            messages.error(
                self.request,
                f'Por favor, corrija os {error_count} erros indicados no formulário.'
            )
        
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Add additional context data for the template.
        """
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        
        # Calculate current completion percentage
        completion_fields = [
            profile.first_name,
            profile.last_name,
            profile.phone,
            profile.birth_date,
            profile.bio
        ]
        completed_fields = sum(1 for field in completion_fields if field)
        completion_percentage = int((completed_fields / len(completion_fields)) * 100)
        
        # Add helpful context
        context.update({
            'completion_percentage': completion_percentage,
            'completed_fields': completed_fields,
            'total_fields': len(completion_fields),
            'is_edit_view': True,
            'cancel_url': reverse_lazy('profiles:detail'),
        })
        
        return context
