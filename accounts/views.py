from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            cf = user_form.cleaned_data
            email = cf['email']
            password = cf['password']
            password2 = cf['password2']
            if password == password2:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Пользователь с таким email уже существует')
                    return render(request, 'accounts/register.html', {'user_form': user_form})
            else:
                messages.error(request, 'Пароли не совпадают')
                return render(request, 'accounts/register.html', {'user_form': user_form})

            new_user = User.objects.create_user(
                first_name = cf['first_name'],
                last_name = cf['last_name'],
                username= email,
                email = email,
                password = password,
            )
            return render(request, 'accounts/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        return render(request, 'accounts/register.html', {'user_form': user_form})
# Create your views here.

@login_required
def profile(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = None
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        if user is None or user.id == request.user.id:
            user_form = UpdateUserForm(instance=request.user, data=request.POST)
            profile_form = UpdateProfileForm(instance=request.user.profile, data=request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Пользователь с таким email уже зарегистрирован')
        return redirect('profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {'user_form': user_form, 'profile_form': profile_form})
    