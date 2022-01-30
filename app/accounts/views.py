from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from .forms import *


class RegisterUser(CreateView):
    '''Регистрация новых пользователей'''
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def form_valid(self, form, *args, **kwargs):
        '''Создание нового пользователя'''
        cf = form.cleaned_data
        email = cf['email']
        password = cf['password']
        password2 = cf['password2']
        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.error(self.request, 'Пользователь с таким email уже существует')
                return render(self.request, 'accounts/register.html', {'form': form})
        else:
            messages.error(self.request, 'Пароли не совпадают')
            return render(self.request, 'accounts/register.html', {'form': form})
        new_user = User.objects.create_user(
            first_name = cf['first_name'],
            last_name = cf['last_name'],
            username= email,
            email = email,
            password = password)
        return render(self.request, 'accounts/register_done.html', {'new_user': new_user})

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('profile')
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, View):
    '''Представление профиля'''
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['user_form'] = UpdateUserForm(instance=self.request.user)
        context['profile_form'] = UpdateProfileForm(instance=self.request.user.profile)
        return context

    def post(self, request):
        '''Обновление профиля'''
        email = request.user.email
        if request.POST['email']:
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
                user_form.save(commit=False)
                request.user.username = email
                request.user.email = email
                request.user.save() 
                profile_form.save()
                messages.success(request, 'Профиль успешно обновлен')
        else:
            messages.error(request, 'Пользователь с таким email уже зарегистрирован')
        return redirect('profile')

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data())