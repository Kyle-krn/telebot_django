from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from .forms import *
from .models import *

User = get_user_model()


class RegisterTest(TestCase):
    '''accounts/register/ (name='register')'''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='seller1', password='password', email='old_user@mail.ru')
        
    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.user)
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        '''Тест добавления нового пользователя'''
        data = {
            'first_name': 'Vlad',
            'last_name': 'Ivanov',
            'email': 'test@mail.ru',
            'password': 'MyPassword123Psy',
            'password2': 'OtherPassword'
        }
        response = self.client.post(reverse('register'), data)  # Пароли не совпадают
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=data['email']).exists())

        data['email'] = self.user.email
        data['password2'] = data['password']
        response = self.client.post(reverse('register'), data)  # Пользователь с таким e-mail уже существует
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, User.objects.filter(email=data['email']).count())

        data['email'] = 'test@mail.ru'          
        response = self.client.post(reverse('register'), data)  # Правильные данные
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_context(self):
        '''Тест контекста'''
        response = self.client.get(reverse('register'))
        self.assertIsInstance(response.context['form'], UserRegistrationForm)


class ProfileTest(TestCase):
    '''accounts/profile/ (name='profile')'''
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='User', password='password', email='test@mail.ru', first_name='TestName', last_name='TestLastName')
    
    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        '''Тест изменения профиля и данных юзера'''
        data = {
            'first_name' : 'New name',
            'last_name' : 'New last name',
            'email': 'new_email@mail.ru',
            'phone_number' : '79006754531',
            'address': 'street Kolotushkina',
            'postal_code': '429950',
            'city': 'DefaultCity'
        }
        self.client.force_login(self.user)
        self.client.post(reverse('profile'), data)
        self.assertFalse(User.objects.filter(email=self.user.email).exists())
        user = User.objects.get(email=data['email'])
        self.assertEqual(user.first_name, data['first_name'])
        self.assertEqual(user.last_name, data['last_name'])
        self.assertEqual(user.email, data['email'])
        self.assertEqual(user.username, data['email'])
        self.assertEqual(user.profile.phone_number, data['phone_number'])
        self.assertEqual(user.profile.postal_code, data['postal_code'])
        self.assertEqual(user.profile.address, data['address'])
        self.assertEqual(user.profile.city, data['city'])

        

    