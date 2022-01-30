from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from main_app.models import *
import os
from .views import get_cart

User = get_user_model()

class CartDetailTest(TestCase):
    '''Тест корзины'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='firstcategory', photo=image, max_count_product=10)
        self.category_1 = Category.objects.create(name='secondcategory', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='firstsubcategory', photo=image, category=self.category)
        self.subcategory_1 = SubCategory.objects.create(name='secondsubcategory', photo=image, category=self.category_1)
        self.product = Product.objects.create(title='firstproduct', photo=image, price=Decimal('100.00'), count=10, weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.product_1 = Product.objects.create(title='secondproduct', photo=image, price=Decimal('150.00'), count=30, weight=20, description='descrpit',  subcategory=self.subcategory_1, )

    def test_requared(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
    
    def test_add_many_count_in_cart(self):
        '''Тест - добавление большего кол-ва товара в корзину чем есть на складе'''
        data = {'quantity': 100}
        response = self.client.post(reverse('cart:cart_add', args=(self.product.pk,)), data)
        request = response.wsgi_request
        cart = get_cart(request)
        product_id = str(self.product.pk)
        self.assertTrue(product_id in cart)
        self.assertEqual(cart[product_id]['quantity'], self.product.count)

    def test_product_in_cart(self):
        '''Добавление товра в корзину'''
        data = {'quantity': 5}
        response = self.client.post(reverse('cart:cart_add', args=(self.product.pk,)), data)
        request = response.wsgi_request
        cart = get_cart(request)
        product_id = str(self.product.pk)
        self.assertTrue(product_id in cart)
        self.assertEqual(cart[product_id]['quantity'], data['quantity'])

        '''Добавить еще тот же товар в корзину'''
        data_1 = {'quantity': 2}
        response = self.client.post(reverse('cart:cart_add', args=(self.product.pk,)), data_1)
        request = response.wsgi_request
        cart = get_cart(request)
        self.assertTrue(product_id in cart)
        self.assertEqual(cart[product_id]['quantity'], data['quantity']+data_1['quantity'])

        '''Теперь добавим в существующий товар в корзине больше товара чем есть на складе'''
        data_2 = {'quantity': 50}
        response = self.client.post(reverse('cart:cart_add', args=(self.product.pk,)), data_2)
        request = response.wsgi_request
        cart = get_cart(request)
        self.assertTrue(product_id in cart)
        self.assertEqual(cart[product_id]['quantity'], self.product.count)

        '''Изменим кол-во товара в корзине'''
        data_3 = {'quantity': 1, 'overwrite_qty': 'True'}
        response = self.client.post(reverse('cart:cart_add', args=(self.product.pk,)), data_3)
        request = response.wsgi_request
        cart = get_cart(request)
        self.assertTrue(product_id in cart)
        self.assertEqual(cart[product_id]['quantity'], data_3['quantity'])


        '''Добавляем еще 1 товар в корзину'''
        data_4 = {'quantity': 5}
        response = self.client.post(reverse('cart:cart_add', args=(self.product_1.pk,)), data_4)
        request = response.wsgi_request
        cart = get_cart(request)
        product_1_id = str(self.product_1.pk)
        self.assertTrue(product_1_id in cart)
        self.assertEqual(cart[product_1_id]['quantity'], data_4['quantity'])

        '''Теперь удаляем 2ой товар из корзины'''
        response = self.client.post(reverse('cart:cart_remove', args=(self.product_1.pk,)))
        request = response.wsgi_request
        cart = get_cart(request)
        self.assertFalse(product_1_id in cart)

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.category_1.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.subcategory_1.photo.path)
            os.remove(self.product.photo.path)
            os.remove(self.product_1.photo.path)
        except FileNotFoundError:
            pass
