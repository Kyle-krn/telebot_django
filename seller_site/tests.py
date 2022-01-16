from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from datetime import date
from .forms import *
from .models import *
User = get_user_model()


class CreateOrderTest(TestCase):
    '''seller/make_order/ (name='create_order')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')
        self.product = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)
        self.product_2 = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)

    def test_anon_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:create_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:create_order'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_order'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_order'))
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())

    def test_post(self):
        '''Тест добавления нового заказа'''
        self.client.force_login(self.super_user)
        data = {'product_id': [self.product.pk, self.product_2.pk], 'product_count': ['2', '3']}
        self.client.post(reverse('local_shop:create_order'), data)

        self.assertEqual(OfflineSoldProduct.objects.filter(product=self.product).exists(), True)
        self.assertEqual(OfflineSoldProduct.objects.filter(product=self.product_2).exists(), True)

        self.assertEqual(OfflineOrderingProduct.objects.filter().exists(), True)
        
        product = OfflineProduct.objects.get(pk=self.product.pk)
        product_2 = OfflineProduct.objects.get(pk=self.product_2.pk)
        self.assertEqual(product.count, 3)
        self.assertEqual(product_2.count, 2)


class OfflineReceptionProductTest(TestCase):
    '''seller/reception/ (name='create_reception')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True)
        self.category = OfflineCategory.objects.create(name='TestCategory', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='TestSubCategory')
        self.product = OfflineProduct.objects.create(title='TestProduct', purchase_price=100, price=50, count=5, subcategory=self.subcategory)
        self.product_2 = OfflineProduct.objects.create(title='TestProduct', purchase_price=100, price=50, count=5, subcategory=self.subcategory)

    def test_anon_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:create_reception'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:create_reception'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_reception'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_reception'))
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertIsInstance(response.context['form'], OfflineReceptionForm)

    def test_post(self):
        '''Тест добавления приемки'''
        self.client.force_login(self.seller_user)
        data = {'count': 10, 'note': 'note', 'product': self.product.pk}
        self.client.post(reverse('local_shop:create_reception'), data)
        product = OfflineProduct.objects.get(pk=self.product.pk)
        self.assertEqual(OfflineReceptionProduct.objects.all().exists(), True)
        self.assertEqual(product.count, 15)


class RegisterUserTest(TestCase):
    '''seller/register_seller/ (name='register_seller')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)


    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:register_seller'))
        self.assertEqual(response.status_code, 302)
        
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:register_seller'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:register_seller'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:register_seller'))
        self.assertIsInstance(response.context['form'], RegisterUserForm)

    def test_post(self):
        '''Тест создания нового продавца'''
        self.client.force_login(self.super_user)
        data = {'username': 'NewTestUser', 'first_name': 'FirstNameTest', 'last_name': 'LastNameTest', 'password1': 'ItsMyPassword33', 'password2': 'ItsMyPassword33'}
        self.client.post(reverse('local_shop:register_seller'), data)
        self.assertEqual(User.objects.filter(username=data['username']).exists(), True)


class OfflineCategoriesTest(TestCase):
    '''seller/category/ (name='list_category')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:list_category'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:list_category'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_category'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_category'))
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertIsInstance(response.context['category_form'], OffilneCategoryForm)
        self.assertIsInstance(response.context['change_category_form'], OffilneChangeCategoryForm)
        self.assertIsInstance(response.context['change_subcategory_form'], OfflineChangeSubcategoryForm)
        self.assertIsInstance(response.context['sc_form'], OfflineSubcategoryForm)
        
    def test_create_category_post(self):
        '''Тест создания новой категории'''
        self.client.force_login(self.super_user)
        data = {'price_for_seller': 30, 'name': 'TestCategory', 'create_category': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        category = OfflineCategory.objects.last()
        self.assertEqual(category.price_for_seller, data["price_for_seller"])
        self.assertEqual(category.name, data["name"])

    def test_update_category_post(self):
        '''Тест изменения категории'''
        self.client.force_login(self.super_user)
        data = {'price_for_seller': 350, 'name': 'NewNameCategory', 'id': self.category.pk, 'change_category': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        category = OfflineCategory.objects.get(pk=self.category.pk)
        self.assertEqual(category.price_for_seller, data["price_for_seller"])
        self.assertEqual(category.name, data["name"])

    def test_delete_category_post(self):
        '''Тест удаления категории'''
        self.client.force_login(self.super_user)
        data = {'category_pk': self.category.pk, 'delete_category': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        self.assertEqual(OfflineCategory.objects.all().exists(), False)

    def test_create_subcategory_post(self):
        '''Тест создания подкатегории'''
        self.client.force_login(self.super_user)
        data = {'category': self.category.pk, 'name': 'TestSubCategory', 'create_sc': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        subcategory = OfflineSubCategory.objects.last()
        self.assertEqual(subcategory.category.pk, data['category'])
        self.assertEqual(subcategory.name, data['name'])

    def test_update_subcategory_post(self):
        '''Тест обналвения подкатегории'''
        self.client.force_login(self.super_user)
        data = {'category': self.category.pk, 'name': 'TestSubCategory', 'id': self.subcategory.pk, 'change_subcategory': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        subcategory = OfflineSubCategory.objects.get(pk=self.subcategory.pk)
        self.assertEqual(subcategory.category.pk, data['category'])
        self.assertEqual(subcategory.name, data['name'])

    def test_delete_category_post(self):
        '''Тест удаления подкатегории'''
        self.client.force_login(self.super_user)
        data = {'subcategory_pk': self.subcategory.pk, 'delete_subcategory': ''}
        self.client.post(reverse('local_shop:list_category'), data)
        self.assertEqual(OfflineSubCategory.objects.all().exists(), False)


class OfflineCreateProductTest(TestCase):
    '''seller/add_product/ (name='create_product')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:create_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:create_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_product'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Текст контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:create_product')) 
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertIsInstance(response.context['form'], OfflineProductForm)

    def test_post(self):
        '''Тест создания нового товара'''
        self.client.force_login(self.super_user)
        data = {'title': 'TestProduct', 'purchase_price': 20, 'price': 50, 'subcategory': self.subcategory.pk}
        self.client.post(reverse('local_shop:create_product'), data)
        self.assertEqual(OfflineProduct.objects.exists(), True)
        product = OfflineProduct.objects.last()
        self.assertEqual(product.title, data['title'])
        self.assertEqual(product.purchase_price, data['purchase_price'])
        self.assertEqual(product.price, data['price'])
        self.assertEqual(product.subcategory.pk, data['subcategory'])
# Create your tests here.


class OfflineIndexTest(TestCase):
    '''seller/ (name='list_product')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='FirstCategory', price_for_seller=10)
        self.category_1 = OfflineCategory.objects.create(name='SecondCategory', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='FirstSubCategory')
        self.subcategory_1 = OfflineSubCategory.objects.create(category=self.category_1, name='SecondSubCategory')
        self.product = OfflineProduct.objects.create(title='TestFirstProduct', purchase_price=100, price=100, count=5, subcategory=self.subcategory)
        self.product_1 = OfflineProduct.objects.create(title='TestSecondProduct', purchase_price=100, price=50, count=5, subcategory=self.subcategory_1)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:list_product'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:list_product'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_product'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_product'))
        self.assertQuerysetEqual(response.context['product'].order_by('id'), list(OfflineProduct.objects.all()))

        data = {'title': 'TestFirstProduct', 'search': ''}
        response = self.client.get(reverse('local_shop:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product'])

        data = {'category': self.category.pk, 'search': ''}
        response = self.client.get(reverse('local_shop:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product'])

        data = {'subcategory': self.subcategory.pk, 'search': ''}
        response = self.client.get(reverse('local_shop:list_product'), data)
        self.assertFalse(self.product_1 in response.context['product'])

    def test_delete_product_post(self):
        '''Тест удаления продукта'''
        self.client.force_login(self.super_user)
        data = {'pk_p': self.product.pk, 'delete_product': ''}
        self.client.post(reverse('local_shop:list_product'), data)
        self.assertEqual(self.product in OfflineProduct.objects.all(), False)


class OfflineProductAdminTest(TestCase):
    '''seller/product/<int:pk>/ (name='product_detail')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')
        self.product = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:product_detail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:product_detail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:product_detail', args=(self.product.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:product_detail', args=(self.product.pk,)))
        self.assertEqual(response.context['product'], self.product)
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertIsInstance(response.context['reception_form'], OfflineReceptionForProductViewForm)

    def test_update_product_post(self):
        '''Тест обновления товара'''
        self.client.force_login(self.super_user)
        data = {'title': 'NewTestProduct', 'purchase_price': 10, 'price': 100, 'subcategory': self.subcategory.pk, 'update': ''}
        self.client.post(reverse('local_shop:product_detail', args=(self.product.pk,)), data)
        product = OfflineProduct.objects.get(title=data['title'])
        self.assertEqual(product.title, data['title'])
        self.assertEqual(product.purchase_price, data['purchase_price'])
        self.assertEqual(product.price, data['price'])
        self.assertEqual(product.subcategory.pk, data['subcategory'])

    def test_delete_product_post(self):
        '''Тест удаления товара'''
        self.client.force_login(self.super_user)
        data = {'delete': ''}
        self.client.post(reverse('local_shop:product_detail', args=(self.product.pk,)), data)
        self.assertEqual(OfflineProduct.objects.all().exists(), False)
    
    def test_reception_product_post(self):
        '''Тест создания приемки'''
        self.client.force_login(self.super_user) 
        data = {'count': 10, 'note': 'note', 'reception': ''}
        self.client.post(reverse('local_shop:product_detail', args=(self.product.pk,)), data)
        self.assertEqual(OfflineReceptionProduct.objects.all().exists(), True)
        product = OfflineProduct.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, self.product.count+data['count'])  

    def test_liquidated_product_post(self):
        '''Тест создания ликвид. товара (приемка с флагом liquidated=True)'''
        self.client.force_login(self.super_user)
        data = {'count': 10, 'note': 'note', 'liquidated': ''}
        self.client.post(reverse('local_shop:product_detail', args=(self.product.pk,)), data)
        self.assertEqual(OfflineReceptionProduct.objects.all().exists(), True)
        product = OfflineProduct.objects.get(pk=self.product.pk)
        self.assertEqual(product.count, self.product.count-data['count'])


class OfflineOrderAdminTest(TestCase):
    '''seller/list_order/ (name='list_order')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_1_user = User.objects.create(username='seller2', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.seller_group[0].user_set.add(self.seller_1_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')
        self.product = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)
        self.order = OfflineOrderingProduct.objects.create(user=self.seller_user)
        self.sold_product = OfflineSoldProduct.objects.create(title=self.product.title, 
                                                                user=self.seller_user,
                                                                product=self.product, 
                                                                price=self.product.price, 
                                                                count=2, 
                                                                order= self.order,
                                                                price_for_seller=self.product.subcategory.category.price_for_seller,)

        self.order_1 = OfflineOrderingProduct.objects.create(user=self.seller_1_user)
        self.sold_1_product = OfflineSoldProduct.objects.create(title=self.product.title, 
                                                                user=self.seller_1_user,
                                                                product=self.product, 
                                                                price=self.product.price, 
                                                                count=3, 
                                                                order= self.order,
                                                                price_for_seller=self.product.subcategory.category.price_for_seller,)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:list_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:list_order'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_order'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:list_order'))
        self.assertQuerysetEqual(response.context['queryset'], OfflineOrderingProduct.objects.all().order_by('-datetime'))
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertQuerysetEqual(response.context['users'].order_by('id'), User.objects.filter(groups__name='sellers'))
        self.assertIsInstance(response.context['form'], OrderChangeForm)

        data = {'user_id': self.seller_user.id, 'seller_filter': ''}
        response = self.client.get(reverse('local_shop:list_order'), data)
        self.assertEqual(response.context['cash_seller'], 20)
        self.assertFalse(self.order_1 in response.context['queryset'])


    def test_change_order_post(self):
        '''Тест изменения кол-ва товара в заказе'''
        self.client.force_login(self.super_user)
        data = {'count': 10}
        self.client.post(reverse('local_shop:change_order', args=(self.order.pk,)), data)
        sold_product = OfflineSoldProduct.objects.get(pk=self.sold_product.pk)
        self.assertEqual(sold_product.count, data['count'])

    def test_remove_item_order_post(self):
        '''Тест удаления товара из заказа'''
        self.client.force_login(self.super_user)
        self.client.post(reverse('local_shop:remove_item_in_order', args=(self.sold_product.pk,)))
        self.assertFalse(self.sold_product in OfflineSoldProduct.objects.all())
    
    def test_delete_order_post(self):
        '''Тест удаления заказа'''
        self.client.force_login(self.super_user)
        self.client.post(reverse('local_shop:delete_order', args=(self.order.pk,)))
        self.assertFalse(self.sold_product in OfflineSoldProduct.objects.all())
        self.assertFalse(self.order in OfflineOrderingProduct.objects.all())


class OfflineStatisticTest(TestCase):
    '''seller/stat/ (name='statistic')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')
        self.product = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)

        self.reception = OfflineReceptionProduct.objects.create(product=self.product, user=self.super_user, price=self.product.purchase_price, count=10)

        self.liquidated = OfflineReceptionProduct.objects.create(product=self.product, user=self.super_user, price=self.product.purchase_price, count=5, liquidated=True)

        self.order = OfflineOrderingProduct.objects.create(user=self.seller_user)
        self.sold_product = OfflineSoldProduct.objects.create(title=self.product.title, 
                                                                user=self.seller_user,
                                                                product=self.product, 
                                                                price=self.product.price, 
                                                                count=2, 
                                                                order= self.order,
                                                                price_for_seller=self.product.subcategory.category.price_for_seller,)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:statistic'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:statistic'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:statistic'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        stat_dict = {'sold_stat': [int(x or 0) for x in tuple(OfflineSoldProduct.objects.all()  \
                                                    .annotate(sold_sum=F('count') * F('price'))  \
                                                    .aggregate(all_sold_price = Sum('sold_sum'),
                                                    all_sold_count = Sum('count')).values())],
        'reception_stat' : [int(x or 0) for x in tuple(OfflineReceptionProduct.objects.all().filter(liquidated=False)  \
                                                                            .annotate(reception_sum=F('count') * F('price'))  \
                                                                            .aggregate(all_reception_price= Sum('reception_sum'), 
                                                                            all_reception_count=Sum('count')).values())],
        'liquidated_stat' : [int(x or 0) for x in tuple(OfflineReceptionProduct.objects.all().filter(liquidated=True)  \
                                                          .annotate(reception_sum=F('count') * F('price'))  \
                                                          .aggregate(all_reception_price= Sum('reception_sum'), 
                                                           all_reception_count=Sum('count')).values())]}
        stat_dict['all_stat'] = stat_dict['sold_stat'][0] - stat_dict['reception_stat'][0] - stat_dict['liquidated_stat'][0]

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:statistic'))
        self.assertEqual(response.context['stat_dict'], stat_dict)
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertQuerysetEqual(response.context['reception_product'], OfflineProduct.objects.annotate(reception_count=Sum('offlinereceptionproduct__count'))  \
                                                                                              .annotate(reception_sum=F('purchase_price') * F('reception_count'))  \
                                                                                              .order_by('-reception_count'))
        self.assertQuerysetEqual(response.context['sold_product'], OfflineProduct.objects.annotate(sold_count=Sum('offlinesoldproduct__count'))  \
                                                                                         .annotate(sold_sum=F('price') * F('sold_count'))  \
                                                                                         .order_by('-sold_count'))


class OfflineSellerTest(TestCase):
    '''seller/my_sales/ (name='my_sales')'''
    def setUp(self):
        self.client = Client()
        self.seller_user = User.objects.create(username='seller1', password='password')
        self.seller_group = Group.objects.get_or_create(name='sellers')
        self.seller_group[0].user_set.add(self.seller_user)
        self.super_user = User.objects.create(username='admin1', password='password', is_superuser=True, is_staff=True)
        self.category = OfflineCategory.objects.create(name='Category', price_for_seller=10)
        self.subcategory = OfflineSubCategory.objects.create(category=self.category, name='SubCategory')
        self.product = OfflineProduct.objects.create(title='Product', purchase_price=100, price=50, count=5, subcategory=self.subcategory)
        self.order = OfflineOrderingProduct.objects.create(user=self.seller_user)
        self.sold_product = OfflineSoldProduct.objects.create(title=self.product.title, 
                                                                user=self.seller_user,
                                                                product=self.product, 
                                                                price=self.product.price, 
                                                                count=2, 
                                                                order= self.order,
                                                                price_for_seller=self.product.subcategory.category.price_for_seller,)

    def test_requared(self):
        '''Тест доступа'''
        response = self.client.get(reverse('local_shop:my_sales'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:my_sales'))
        self.assertEqual(response.status_code, 200)

        self.client.force_login(self.super_user)
        response = self.client.get(reverse('local_shop:my_sales'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        '''Тест контекста'''
        self.client.force_login(self.seller_user)
        response = self.client.get(reverse('local_shop:my_sales'))
        self.assertQuerysetEqual(response.context['category'], OfflineCategory.objects.all())
        self.assertQuerysetEqual(response.context['queryset'], OfflineOrderingProduct.objects.filter(Q(user=self.seller_user) & Q(datetime__gte=date.today())).order_by('-datetime'))
        self.assertEqual(response.context['sum_for_seller'], 20)