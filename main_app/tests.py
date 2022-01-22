import os
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from main_app.utils import check_price_delivery
from .models import *
from .views import *
from .forms import *

User = get_user_model()


class ListProductTest(TestCase):
    '''Список товаров| /main/ |(name='list_product)'''
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
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertEqual(response.status_code, 302)
       
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:list_product'))
        self.assertQuerysetEqual(response.context['category'].order_by('id'), Category.objects.all())
        self.assertIsInstance(response.context['delete_form'], ProductDeleteForm)
        self.assertQuerysetEqual(response.context['product'].order_by('id'), Product.objects.all())

    def test_search(self):
        '''Тест поиска'''
        self.client.force_login(self.super_user)
        data = {'title': 'firstproduct', 'search': ''}
        response = self.client.get(reverse('admin_panel:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product'])

        data = {'category': self.category.pk, 'search': ''}
        response = self.client.get(reverse('admin_panel:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product']) 

        data = {'subcategory': self.subcategory.pk, 'search': ''}
        response = self.client.get(reverse('admin_panel:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product'])

    def test_post(self):
        '''Тест удаления товара'''
        self.client.force_login(self.super_user)
        response = self.client.post(reverse('admin_panel:list_product'), {'id': self.product.pk})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product in Product.objects.all())

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            pass
        


class CreateProductTest(TestCase):
    '''Создание продукта| /main/create_product/ |(name='create_product')'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=self.image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=self.image, category=self.category)
        
    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:create_product'))
        self.assertQuerysetEqual(response.context['category'], Category.objects.all())
        self.assertIsInstance(response.context['form'], ProductForm)

    def test_post(self):
        '''Тест создания товара'''
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
        except FileNotFoundError:
            pass


class ReceptionProductTest(TestCase):
    '''Приемка товара| /main/reception/ |(name="reception")'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:reception'))
        self.assertQuerysetEqual(response.context['category'], Category.objects.all())
        self.assertIsInstance(response.context['form'], ReceptionForm)

    def test_post(self):
        '''Тест создания приемки'''
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
            pass


class CategoryUpdateTest(TestCase):
    '''Обновление категорий| /main/category/<int:pk>/ |(name='categorydetail')'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест категории'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:categorydetail', args=(self.category.pk,)))
        self.assertIsInstance(response.context['form'], Category_reqForm)

    def test_change_category_post(self):
        '''Тест изменения категории'''
        self.client.force_login(self.super_user)
        initial = {'name': 'change_category', 'max_count_product': 20, 'photo': ''}
        response = self.client.post(reverse('admin_panel:categorydetail', args=(self.category.pk,)), initial)
        category = Category.objects.get(pk=self.category.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(category.name, initial['name'])
        self.assertEqual(category.max_count_product, initial['max_count_product'])

    def test_delete_category_post(self):
        '''Тест удаления категории'''
        self.client.force_login(self.super_user)
        initial = {'delete': ''}
        self.client.post(reverse('admin_panel:categorydetail', args=(self.category.pk,)), initial)
        self.assertFalse(Category.objects.all().exists())

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
        except FileNotFoundError:
            pass


class SubCategoryUpdateTest(TestCase):
    '''Обновление подкатегорий| /main/subcategory/<int:pk>/ |(name='subcategorydetail')'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест категории'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)))
        self.assertIsInstance(response.context['form'], Subcategory_reqForm)

    def test_change_category_post(self):
        '''Тест обновления подкатегории'''
        self.client.force_login(self.super_user)
        initial = {'name': 'change_subcategory', 'photo': ''}
        response = self.client.post(reverse('admin_panel:subcategorydetail', args=(self.category.pk,)), initial)
        subcategory = SubCategory.objects.get(pk=self.subcategory.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(subcategory.name, initial['name'])

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
        except FileNotFoundError:
            pass


class CategoriesTest(TestCase):
    '''Создание и список категорий| /main/create_category/ |(name='create_category')'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:create_category'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:create_category'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:create_category'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:create_category'))
        self.assertQuerysetEqual(response.context['queryset'], Category.objects.all())
        self.assertIsInstance(response.context['category_form'], CategoryForm)
        self.assertIsInstance(response.context['sc_form'], SubcategoryForm)

    def test_create_category_post(self):
        '''Тест создания категории'''
        self.client.force_login(self.super_user)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        initial = {'name': 'категория', 'max_count_product': 20, 'photo': image, 'create_category': ''}
        response = self.client.post(reverse('admin_panel:create_category'), initial)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name=initial['name']).exists())
        category = Category.objects.get(name=initial['name'])
        self.assertEqual(category.name, initial['name'])
        self.assertEqual(category.max_count_product, initial['max_count_product'])
        
        '''Тест создания подкатегории'''
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        initial = {'name': 'подкатегория', 'photo': image, 'category': category.pk, 'create_sc': ''}
        response = self.client.post(reverse('admin_panel:create_category'), initial)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SubCategory.objects.filter(name=initial['name']).exists())
        subcategory = SubCategory.objects.get(name=initial['name'])
        self.assertEqual(subcategory.name, initial['name'])
        self.assertEqual(subcategory.category, category)
        category.photo.delete()     
        subcategory.photo.delete()


class QiwiOrderTest(TestCase):
    '''Киви| /main/qiwi/ |(name="control_qiwi")'''
    def setUp(self) -> None:
        self.client = Client()
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

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:qiwi_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:qiwi_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:qiwi_order'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:qiwi_order'))
        self.assertQuerysetEqual(response.context['queryset'], OrderingProduct.objects.filter(qiwi_bool=True).order_by('-datetime'))

    def test_reservation(self):
        '''Тест бронирования'''
        product = Product.objects.get(pk=self.product.pk)
        product1 = Product.objects.get(pk=self.product1.pk)
        self.assertEqual(product.count, 15)
        self.assertEqual(product1.count, 20)
        self.pay_data.cancel_reservation()
        product = Product.objects.get(pk=self.product.pk)
        product1 = Product.objects.get(pk=self.product1.pk)
        self.assertEqual(product.count, 25)
        self.assertEqual(product1.count, 25)

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.product.photo.path)
            os.remove(self.product1.photo.path)
        except FileNotFoundError:
            pass


class NoPaidOrderTest(TestCase):
    '''Неоплаченные заказы | /main/new_order/ |(name="no_paid_order")'''
    def setUp(self) -> None:
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.super_user = User.objects.create(username='admin1', password='password', is_staff=True)
        image = SimpleUploadedFile(name='test_image.jpg', content=open(r'static\img\test.jpg', 'rb').read(), content_type='image/jpeg')
        self.category = Category.objects.create(name='category', photo=image, max_count_product=10)
        self.subcategory = SubCategory.objects.create(name='subcategory', photo=image, category=self.category)
        self.product = Product.objects.create(title='product', photo=image, price=Decimal('100.00'), weight=100, description='descrpit',  subcategory=self.subcategory, )
        self.reception = ReceptionProduct.objects.create(price=100, count=25, product=self.product)
        self.telegram_user = TelegramUser.objects.create(chat_id='666666', post_index=429950)
        self.cart_item = TelegramProductCartCounter.objects.create(user=self.telegram_user, product=self.product, count=10, counter=False)
        self.cart  = TelegramProductCartCounter.objects.filter(Q(user=self.telegram_user) & Q(counter=False)) 
        self.weight = sum([x.count * x.product.weight for x in self.cart])
        self.delivery_pay = check_price_delivery(post_index=self.telegram_user.post_index, weight=self.weight)
        self.product_pay = sum([x.count * x.product.price for x in self.cart])  
        self.order = OrderingProduct.objects.create(user=self.telegram_user, delivery_pay=self.delivery_pay, fio=self.telegram_user.fio, address=self.telegram_user.address, number=self.telegram_user.number, post_index=self.telegram_user.post_index, payment_bool=False, qiwi_bool=False)
        for item in self.cart:
            self.sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count, payment_bool=True, order=self.order)
        self.order.set_order_price()

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:no_paid_order'))
        self.assertQuerysetEqual(response.context['queryset'], OrderingProduct.objects.filter(Q(payment_bool=False) & Q(qiwi_bool=False)).order_by('-datetime'))


    def test_change_count_order_item(self):
        '''Тест измнения кол-ва товара в заказе'''
        self.client.force_login(self.super_user) # change_item_order
        initial = {'count': 30}
        sold_product = SoldProduct.objects.get(product=self.product)
        self.client.post(reverse('admin_panel:change_item_bot_order', args=(sold_product.pk,)), initial)
        sold_product = SoldProduct.objects.get(product=self.product)
        self.assertEqual(sold_product.count, initial['count'])

    def test_remove_order_item(self):
        '''Тест удаления товара из заказа'''
        self.client.force_login(self.super_user) # change_item_order
        sold_product = SoldProduct.objects.get(product=self.product)
        self.client.post(reverse('admin_panel:remove_item_bot_order', args=(sold_product.pk,)))
        order = OrderingProduct.objects.get(pk=self.order.pk)
        self.assertFalse(order.soldproduct.all().exists())

    def test_delete_order(self):
        '''Тест удаления заказа'''
        self.client.force_login(self.super_user)
        order = OrderingProduct.objects.get(pk=self.order.pk)
        self.client.post(reverse('admin_panel:delete_bot_order', args=(order.pk,)))
        self.assertFalse(OrderingProduct.objects.all().exists())

    def test_confirm_order(self):
        '''Тест подтверждения оплаты заказа'''
        self.client.force_login(self.super_user)
        initial = {'id': self.order.pk}
        self.client.post(reverse('admin_panel:no_paid_order'), initial)
        order = OrderingProduct.objects.get(pk=self.order.pk)
        product = Product.objects.get(pk=self.product.pk)
        self.assertTrue(order.payment_bool)
        self.assertEqual(product.count, 15)

    def tearDown(self):
            try:
                os.remove(self.category.photo.path)
                os.remove(self.subcategory.photo.path)
                os.remove(self.product.photo.path)
            except FileNotFoundError:
                pass


class ProductViewTest(TestCase):
    '''Детальное прдеставление продукта | /main/product/<int:pk> |(name='productdetail")'''
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

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 200)
        
    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('admin_panel:productdetail', args=(self.product.pk,)))
        self.assertEqual(response.context['product'], self.product)
        self.assertEqual(response.context['reservation_count'], self.cart_item.count)
        self.assertQuerysetEqual(response.context['category'], Category.objects.all())
        self.assertIsInstance(response.context['reception_form'], ReceptionForProductViewForm)
        self.assertIsInstance(response.context['product_form'], Product_reqForm)

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
        '''Тест обновления товара'''
        self.client.force_login(self.super_user)
        initial = {'title': 'изменить название', 'photo': '', 'description': 'изменить описание', 'price': 140, 'subcategory': self.subcategory1.pk, 'weight': 200, 'update': ''}
        self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.title, initial['title'])
        self.assertEqual(product.description, initial['description'])
        self.assertEqual(product.price, initial['price'])
        self.assertEqual(product.weight, initial['weight'])
        self.assertEqual(product.subcategory, self.subcategory1)

    def test_delete_post(self):
        '''Тест удаления товара'''
        self.client.force_login(self.super_user)
        initial = {'delete': ''}
        self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        self.assertFalse(Product.objects.all().exists())

    def test_reception_post(self):
        '''Тест добавления приемки'''
        self.client.force_login(self.super_user)
        initial = {'price': 300, 'count': 40, 'note': 'заметка', 'reception': ''}
        self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, 55)
        self.assertTrue( ReceptionProduct.objects.filter(count=initial['count']).exists())

    def test_liq_post(self):
        '''Тест добавления ликвид. товара'''
        self.client.force_login(self.super_user)
        initial = {'price': 300, 'count': 5, 'note': 'заметка', 'liquidated': ''}
        self.client.post(reverse('admin_panel:productdetail', args=(self.product.pk,)), initial)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, 10)
        self.assertTrue( ReceptionProduct.objects.filter(Q(count=initial['count']) & Q(liquidated=True)).exists())

    def tearDown(self):
        try:
            os.remove(self.category.photo.path)
            os.remove(self.subcategory.photo.path)
            os.remove(self.subcategory1.photo.path)
            os.remove(self.product.photo.path)
        except FileNotFoundError:
            pass


    
    


