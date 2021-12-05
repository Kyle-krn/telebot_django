from itertools import product
import os
from django.test import TestCase, RequestFactory, Client

from main_app.utils import check_price_delivery
from .models import *
from .views import *
from .forms import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from PIL import Image
from django.conf import settings
import tempfile


User = get_user_model()


class ListProductTest(TestCase):
    '''Тест-модель для представления IndexView'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), count=10, weight=100, description='descrpit',  subcategory=self.subcategory, )

    def test_seller_requared(self):
        '''Проверка '''
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertEqual(response.status_code, 302)


    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.force_login(self.super_user)
        response = self.client.post(reverse('admin_panel:list_product'), {'id': self.product.pk})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.all().count())

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            print('file not found')
        


class CreateProductTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=self.image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=self.image, category=self.category)
        
    def test_seller_requared(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        self.client.force_login(self.super_user)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        response = self.client.post(reverse('admin_panel:create_product'), {'title': 'Название', 'photo': image, 'description': 'описание', 'price': 10, 'subcategory': self.subcategory.pk, 'weight': 100})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(title='Название').exists())
        product = Product.objects.get(title='Название')
        self.assertEqual(product.pk_for_telegram, f"p||{product.pk}")
        product.photo.delete()

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            # os.remove(self.product.photo.path)
        except FileNotFoundError:
            print('file not found')



class ReceptionProductTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )


    def test_seller_requared(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertEqual(response.status_code, 302)


    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertEqual(response.status_code, 200)


    def test_post(self):
        self.client.force_login(self.super_user)
        initial = {'price': 100, 'count': 15, 'note': 'заметка', 'product': self.product.pk}
        response = self.client.post(reverse('admin_panel:reception'), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ReceptionProduct.objects.all().exists())
        self.assertEqual(product.count, initial['count'])


    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            print('file not found')


class CategoryUpdateTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)

    def test_seller_requared(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_change_category_post(self):
        self.client.force_login(self.super_user)
        initial = {'name': 'change_category', 'max_count_product': 20, 'photo': ''}
        response = self.client.post(reverse('admin_panel:categorydetail', args=(self.category.pk,)), initial)
        category = Category.objects.get(pk=self.category.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(category.name, initial['name'])
        self.assertEqual(category.max_count_product, initial['max_count_product'])

    def test_delete_categorry_post(self):
        self.client.force_login(self.super_user)
        initial = {'delete': ''}
        response = self.client.post(reverse('admin_panel:categorydetail', args=(self.category.pk,)), initial)
        self.assertFalse(Category.objects.all().exists())

    
    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            # os.remove(self.subcategory.photo.path)
            # os.remove(self.product.photo.path)
        except FileNotFoundError:
            print('file not found')


class SubCategoryUpdateTest(TestCase):
    def setUp(self) -> None:
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        # self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )

    def test_seller_requared(self):
        c = Client()
        c.force_login(self.seller_user)
        response = c.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        c = Client()
        c.force_login(self.super_user)
        response = c.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 200)


    def test_change_category_post(self):
        c = Client()
        c.force_login(self.super_user)
        initial = {'name': 'change_subcategory', 'photo': ''}
        response = c.post(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)), initial)
        subcategory = SubCategory.objects.get(pk=self.subcategory.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(subcategory.name, initial['name'])

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            # os.remove(self.product.photo.path)
        except FileNotFoundError:
            print('file not found')


class CategoriesTest(TestCase):
    def setUp(self) -> None:
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        # self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        # self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        # self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )

    def test_seller_requared(self):
        c = Client()
        c.force_login(self.seller_user)
        response = c.get(reverse('admin_panel:create_category'))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        c = Client()
        c.force_login(self.super_user)
        response = c.get(reverse('admin_panel:create_category'))
        self.assertEqual(response.status_code, 200)

    def test_create_category_post(self):
        c = Client()
        c.force_login(self.super_user)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        initial = {'name': 'категория', 'max_count_product': 20, 'photo': image, 'create_category': ''}
        response = c.post(reverse('admin_panel:create_category'), initial)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name=initial['name']).exists())
        category = Category.objects.get(name=initial['name'])
        self.assertEqual(category.name, initial['name'])
        self.assertEqual(category.max_count_product, initial['max_count_product'])
        

        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        initial = {'name': 'подкатегория', 'photo': image, 'category': category.pk, 'create_sc': ''}
        response = c.post(reverse('admin_panel:create_category'), initial)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SubCategory.objects.filter(name=initial['name']).exists())
        subcategory = SubCategory.objects.get(name=initial['name'])
        self.assertEqual(subcategory.name, initial['name'])
        self.assertEqual(subcategory.category, category)
        
        category.photo.delete()     
        subcategory.photo.delete()


class QiwiOrderTest(TestCase):
    def setUp(self) -> None:
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.reception = ReceptionProduct.objects.create(price=100, count=25, product=self.product)
        self.product1 = Product.objects.create(title='product_1', photo=image, price=Decimal('50.00'), weight=200, description='descrpit',  subcategory=self.subcategory, )
        self.reception1 = ReceptionProduct.objects.create(price=100, count=25, product=self.product1)
        self.telegram_user = TelegramUser.objects.create(chat_id='666666', post_index=429950)

        self.cart_item = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product, count=10, counter=False)
        self.cart_item1 = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product1, count=5, counter=False)

        self.cart  = TelegramProductCartCounter.objects.filter(Q(user=self.telegram_user) & Q(counter=False)) 

        self.weight = sum([x.count * x.product.weight for x in self.cart])
        
        self.delivery_pay = check_price_delivery(post_index=self.telegram_user.post_index, weight=self.weight)
        self.product_pay = sum([x.count * x.product.price for x in self.cart])  

        self.pay_data = PayProduct.objects.create(user=self.telegram_user, pay_comment='vfvd', delivery_pay=self.delivery_pay, product_pay=self.product_pay)

        self.order = OrderingProduct.objects.create(user=self.telegram_user, delivery_pay=self.pay_data.delivery_pay, fio=self.telegram_user.fio, address=self.telegram_user.address, number=self.telegram_user.number, post_index=self.telegram_user.post_index, payment_bool=True, qiwi_bool=True)
        for item in self.cart:
            self.sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count, payment_bool=True, order=self.order)
        self.order.set_order_price()

    def test_seller_requared(self):
        c = Client()
        c.force_login(self.seller_user)
        response = c.get(reverse('admin_panel:qiwi_order'))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        c = Client()
        c.force_login(self.super_user)
        response = c.get(reverse('admin_panel:qiwi_order'))
        self.assertEqual(response.status_code, 200)


    def test_reservation(self):
        product = Product.objects.get(pk=self.product.pk)
        product1 = Product.objects.get(pk=self.product1.pk)
        self.assertEqual(product.count, 15)
        self.assertEqual(product1.count, 20)

        self.pay_data.cancel_reservation()
        
        product = Product.objects.get(pk=self.product.pk)
        product1 = Product.objects.get(pk=self.product1.pk)
        self.assertEqual(product.count, 25)
        self.assertEqual(product1.count, 25)


    def test_add_postal_code_post(self):
        c = Client()
        c.force_login(self.super_user)
        initial = {'track_code': '3534654234'}
        response = c.post(reverse('admin_panel:add_track_code_in_order', args=(self.order.pk,)), initial)
        order = OrderingProduct.objects.get(pk=self.order.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(order.track_code, initial['track_code'])


    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
            os.remove(self.product1.photo.path)
        except FileNotFoundError:
            print('file not found')


class NoPaidOrderTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.reception = ReceptionProduct.objects.create(price=100, count=25, product=self.product)
        # self.product1 = Product.objects.create(title='product_1', photo=image, price=Decimal('50.00'), weight=200, description='descrpit',  subcategory=self.subcategory, )
        # self.reception1 = ReceptionProduct.objects.create(price=100, count=25, product=self.product1)
        self.telegram_user = TelegramUser.objects.create(chat_id='666666', post_index=429950)

        self.cart_item = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product, count=10, counter=False)
        # self.cart_item1 = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product1, count=5, counter=False)

        self.cart  = TelegramProductCartCounter.objects.filter(Q(user=self.telegram_user) & Q(counter=False)) 

        self.weight = sum([x.count * x.product.weight for x in self.cart])
        
        self.delivery_pay = check_price_delivery(post_index=self.telegram_user.post_index, weight=self.weight)
        self.product_pay = sum([x.count * x.product.price for x in self.cart])  

        self.order = OrderingProduct.objects.create(user=self.telegram_user, delivery_pay=self.delivery_pay, fio=self.telegram_user.fio, address=self.telegram_user.address, number=self.telegram_user.number, post_index=self.telegram_user.post_index, payment_bool=False, qiwi_bool=False)
        for item in self.cart:
            self.sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count, payment_bool=True, order=self.order)
        self.order.set_order_price()

    def test_seller_requared(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertEqual(response.status_code, 200)

    def test_change_count_order_item(self):
        self.client.force_login(self.super_user) # change_item_order
        initial = {'count': 30}
        sold_product = SoldProduct.objects.get(product=self.product)
        response = self.client.post(reverse('admin_panel:change_item_order', args=(sold_product.pk,)), initial)
        sold_product = SoldProduct.objects.get(product=self.product)
        self.assertEqual(sold_product.count, initial['count'])

    def test_remove_order_item(self):
        self.client.force_login(self.super_user) # change_item_order
        sold_product = SoldProduct.objects.get(product=self.product)
        response = self.client.post(reverse('admin_panel:remove_item_order', args=(sold_product.pk,)))
        order = OrderingProduct.objects.get(pk=self.order.pk)
        # self.assertEqual(order.soldproduct_set.all().count(), 1)
        self.assertFalse(order.soldproduct.all().exists())

    def test_delete_order(self):
        self.client.force_login(self.super_user)
        order = OrderingProduct.objects.get(pk=self.order.pk)
        response = self.client.post(reverse('admin_panel:delete_order', args=(order.pk,)))
        self.assertFalse(OrderingProduct.objects.all().exists())

    def test_confirm_order(self):
        self.client.force_login(self.super_user)
        initial = {'id': self.order.pk}
        response = self.client.post(reverse('admin_panel:no_paid_order'), initial)
        order = OrderingProduct.objects.get(pk=self.order.pk)
        product = Product.objects.get(pk=self.product.pk)
        self.assertTrue(order.payment_bool)
        self.assertEqual(product.count, 15)


    def tearDown(self):
            try:
                os.remove(self.category.photo.path)
                os.remove(self.subcategory.photo.path)
                os.remove(self.product.photo.path)
                # os.remove(self.product1.photo.path)
            except FileNotFoundError:
                print('file not found')


class ProductViewTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.subcategory1 = SubCategory.objects.create(name='subcategory1', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.reception = ReceptionProduct.objects.create(price=100, count=25, product=self.product)
        self.telegram_user = TelegramUser.objects.create(chat_id='666666', post_index=429950)

        self.cart_item = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product, count=10, counter=False)

        self.cart  = TelegramProductCartCounter.objects.filter(Q(user=self.telegram_user) & Q(counter=False)) 

        self.weight = sum([x.count * x.product.weight for x in self.cart])
        
        self.delivery_pay = check_price_delivery(post_index=self.telegram_user.post_index, weight=self.weight)
        self.product_pay = sum([x.count * x.product.price for x in self.cart])  

        self.pay_data = PayProduct.objects.create(user=self.telegram_user, pay_comment='vfvd', delivery_pay=self.delivery_pay, product_pay=self.product_pay)

        # self.order = OrderingProduct.objects.create(user=self.telegram_user, delivery_pay=self.pay_data.delivery_pay, fio=self.telegram_user.fio, address=self.telegram_user.address, number=self.telegram_user.number, post_index=self.telegram_user.post_index, payment_bool=True, qiwi_bool=True)
        # for item in self.cart:
        #     self.sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count, payment_bool=True, order=self.order)
        # self.order.set_order_price()

    def test_seller_requared(self):
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_admin_requared(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reservation_count'], self.cart_item.count)

    def test_del_pay_data(self):
        self.client.force_login(self.super_user)
        self.order = OrderingProduct.objects.create(user=self.telegram_user, delivery_pay=self.pay_data.delivery_pay, fio=self.telegram_user.fio, address=self.telegram_user.address, number=self.telegram_user.number, post_index=self.telegram_user.post_index, payment_bool=True, qiwi_bool=True)
        for item in self.cart:
            self.sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count, payment_bool=True, order=self.order)
        self.order.set_order_price()
        self.pay_data.delete()
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertFalse(response.context['reservation_count'])

    def test_update_post(self):
        self.client.force_login(self.super_user)
        initial = {'title': 'изменить название', 'photo': '', 'description': 'изменить описание', 'price': 140, 'subcategory': self.subcategory1.pk, 'weight': 200, 'update': ''}
        response = self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.title, initial['title'])
        self.assertEqual(product.description, initial['description'])
        self.assertEqual(product.price, initial['price'])
        self.assertEqual(product.weight, initial['weight'])
        self.assertEqual(product.subcategory, self.subcategory1)

    def test_delete_post(self):
        self.client.force_login(self.super_user)
        initial = {'delete': ''}
        response = self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        self.assertFalse(Product.objects.all().exists())

    def test_reception_post(self):
        self.client.force_login(self.super_user)
        initial = {'price': 300, 'count': 40, 'note': 'заметка', 'reception': ''}
        response = self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, 55)
        self.assertTrue( ReceptionProduct.objects.filter(count=initial['count']).exists())

    def test_liq_post(self):
        self.client.force_login(self.super_user)
        initial = {'price': 300, 'count': 5, 'note': 'заметка', 'liquidated': ''}
        response = self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, 10)
        self.assertTrue( ReceptionProduct.objects.filter(Q(count=initial['count']) & Q(liquidated=True)).exists())


    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.subcategory1.photo.path)
            os.remove(self.product.photo.path)
            # os.remove(self.product1.photo.path)
        except FileNotFoundError:
            print('file not found')


    
    


