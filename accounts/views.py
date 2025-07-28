from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def profile_view(request):
    """View para exibir e editar perfil do usuário"""
    if request.method == 'POST':
        # Handle profile update
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        
        if user.user_type == 'driver':
            user.driving_license = request.POST.get('driving_license', user.driving_license)
        
        user.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('accounts:profile')
    
    context = {
        'user': request.user,
        'password_form': PasswordChangeForm(request.user)
    }
    return render(request, 'accounts/profile.html', context)
