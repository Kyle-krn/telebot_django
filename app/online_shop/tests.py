from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from main_app.models import *
from .forms import *
from cart.forms import CartAddProductForm
from decimal import Decimal
import os

User = get_user_model()

class ProductListTest(TestCase):
    '''Список товаров| host.com/ (name='online_shop:product_list')'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='firstcategory', photo=image, max_count_product=10)
        self.category_1 = Category.objects.create(name='secondcategory', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='firstsubcategory', photo=image, category=self.category)
        self.subcategory_1 = SubCategory.objects.create(name='secondsubcategory', photo=image, category=self.category_1)
        self.subcategory_1_1 = SubCategory.objects.create(name='second_1_subcategory', photo=image, category=self.category_1)
        self.product = Product.objects.create(title='firstproduct', photo=image, price=Decimal('100.00'), count=10, weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.product_1 = Product.objects.create(title='secondproduct', photo=image, price=Decimal('150.00'), count=30, weight=20, description='descrpit',  subcategory=self.subcategory_1, )
        self.product_1_1 = Product.objects.create(title='second_1_product', photo=image, price=Decimal('150.00'), count=30, weight=20, description='descrpit',  subcategory=self.subcategory_1_1, )

    def test_requared(self):
        response = self.client.get(reverse('online_shop:product_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_context(self):
        '''Все товары'''
        response = self.client.get(reverse('online_shop:product_list'))
        self.assertQuerysetEqual(response.context['categories'].order_by('id'), Category.objects.all())
        self.assertQuerysetEqual(response.context['products'].order_by('id'), Product.objects.all())
        self.assertEqual(response.context['requested_category'], None)
        self.assertEqual(response.context['requested_subcategory'], None)

        '''Товары категории'''
        response = self.client.get(reverse('online_shop:product_list_by_category', args=(self.category_1.slug,)))
        self.assertQuerysetEqual(response.context['products'].order_by('id'), Product.objects.filter(subcategory__category=self.category_1))
        self.assertEqual(response.context['requested_category'], self.category_1)
        self.assertEqual(response.context['requested_subcategory'], None)

        '''Товары подкатегории'''
        response = self.client.get(reverse('online_shop:product_list_by_subcategory', args=(self.category_1.slug, self.subcategory_1)))
        self.assertQuerysetEqual(response.context['products'].order_by('id'), Product.objects.filter(subcategory=self.subcategory_1))
        self.assertEqual(response.context['requested_category'], self.category_1)
        self.assertEqual(response.context['requested_subcategory'], self.subcategory_1)

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.category_1.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.subcategory_1.photo.path)
            os.remove(self.subcategory_1_1.photo.path)
            os.remove(self.product.photo.path)
            os.remove(self.product_1_1.photo.path)
        except FileNotFoundError:
            pass


class ProdutDetailTest(TestCase):
    '''Детальное представление товара| product/<slug:slug> (name="online_shop:product_detail")'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='firstcategory', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='firstsubcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='firstproduct', photo=image, price=Decimal('100.00'), count=10, weight=100, description='descrpit',  subcategory=self.subcategory, )
    
    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('online_shop:product_detail', args=(self.product.slug,)))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест конеткста'''
        response = self.client.get(reverse('online_shop:product_detail', args=(self.product.slug,)))
        self.assertEqual(response.context['product'], self.product)
        self.assertIsInstance(response.context['review_form'], ReviewForm)
        self.assertIsInstance(response.context['cart_product_form'], CartAddProductForm)

    def test_add_review(self):
        '''Тест добавления отзыва'''
        data = {
            'text': 'TestReview',
            'rating': 5
        }
        response = self.client.post(reverse('online_shop:product_detail', args=(self.product.slug,)), data)
        self.assertTrue(self.product.reviews.all().exists())
        review = self.product.reviews.all()[0]
        self.assertEqual(review.text, data['text'])
        self.assertEqual(review.rating, data['rating'])    

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            pass

class OrderCreateTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='firstcategory', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='firstsubcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='firstproduct', photo=image, price=Decimal('100.00'), count=10, weight=100, description='descrpit',  subcategory=self.subcategory, )
    
    def test_requared(self):
        response = self.client.get(reverse('online_shop:order_create'))
        self.assertEqual(response.status_code, 200)


    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            pass
