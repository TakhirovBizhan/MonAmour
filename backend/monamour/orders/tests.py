# orders/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from store.models import Painting, Artist, Gallery
from orders.models import Cart, Order, OrderItem
import datetime

User = get_user_model()

class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass123')
        self.other_user = User.objects.create_user(username='user2', password='pass123')
        self.artist = Artist.objects.create(name="Artist1", biography="Bio")
        self.gallery = Gallery.objects.create(name="Gallery1")
        self.painting1 = Painting.objects.create(
            title="Test Painting 1",
            artist=self.artist,
            gallery=self.gallery,
            price="100.00",
            status='available'
        )
        self.painting2 = Painting.objects.create(
            title="Test Painting 2",
            artist=self.artist,
            gallery=self.gallery,
            price="150.00",
            status='available'
        )
        # Cart items for both users
        self.cart_item_user = Cart.objects.create(user=self.user, painting=self.painting1)
        self.cart_item_other = Cart.objects.create(user=self.other_user, painting=self.painting2)
        self.client = APIClient()

    def test_add_to_cart(self):
        self.client.force_authenticate(user=self.user)
        url = '/api/carts/'
        data = {'painting_id': str(self.painting1.id)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Cart.objects.filter(user=self.user, painting=self.painting1).exists())

    def test_remove_from_cart(self):
        cart_item = Cart.objects.create(user=self.user, painting=self.painting1)
        self.client.force_authenticate(user=self.user)
        url = f'/api/carts/{cart_item.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cart.objects.filter(pk=cart_item.id).exists())

    def test_list_cart_only_returns_own_items(self):
        """
        При GET /api/carts/ пользователь должен видеть только свои записи в корзине,
        даже если в БД есть записи других пользователей.
        """
        self.client.force_authenticate(user=self.user)
        url = '/api/carts/'
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        body = response.json()
        # Если пагинация: dict с 'results'
        if isinstance(body, dict) and 'results' in body:
            items = body['results']
        else:
            items = body
        # Проверяем, что среди возвращённых нет записи другого пользователя
        returned_ids = {item['id'] for item in items}
        self.assertIn(str(self.cart_item_user.id), returned_ids)
        self.assertNotIn(str(self.cart_item_other.id), returned_ids)


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user2', password='pass123')
        self.artist = Artist.objects.create(name="Artist2", biography="Bio2")
        self.gallery = Gallery.objects.create(name="Gallery2")
        self.paint1 = Painting.objects.create(
            title="P1", artist=self.artist, gallery=self.gallery,
            price="50.00", status='available'
        )
        self.paint2 = Painting.objects.create(
            title="P2", artist=self.artist, gallery=self.gallery,
            price="75.00", status='available'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_order_single_painting(self):
        url = '/api/orders/'
        payload = {
            "street": "Some St",
            "house_number": "10",
            "city": "City",
            "postal_code": "12345",
            "payment_method": "card",
            "phone_number": "+70000000000",
            "painting_ids": [str(self.paint1.id)],
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        order = Order.objects.get(id=data['id'])
        self.assertEqual(order.user, self.user)
        items = OrderItem.objects.filter(order=order)
        self.assertEqual(items.count(), 1)
        self.assertEqual(str(items.first().painting.id), str(self.paint1.id))

    def test_create_order_multiple_paintings(self):
        url = '/api/orders/'
        payload = {
            "street": "Other St",
            "house_number": "20",
            "city": "Town",
            "postal_code": "54321",
            "payment_method": "cash",
            "phone_number": "80000000000",
            "painting_ids": [str(self.paint1.id), str(self.paint2.id)],
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        order = Order.objects.get(id=data['id'])
        items = OrderItem.objects.filter(order=order)
        self.assertEqual(items.count(), 2)
        ids = {str(item.painting.id) for item in items}
        self.assertSetEqual(ids, {str(self.paint1.id), str(self.paint2.id)})

    def test_order_access_rights(self):
        other = User.objects.create_user(username='other', password='pass123')
        order = Order.objects.create(
            user=other,
            street="A", house_number="1", city="C", postal_code="000",
            payment_method="card", phone_number="123"
        )
        # как другой пользователь пробуем получить чужой заказ
        self.client.force_authenticate(user=self.user)
        url = f'/api/orders/{order.id}/'
        response = self.client.get(url)
        # Обычный пользователь не должен видеть чужой заказ: 404 или 403
        self.assertIn(response.status_code, (status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN))


class ArtistReviewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='revuser', password='pass123')
        self.artist = Artist.objects.create(name="ArtistRev", biography="BioRev")
        self.client = APIClient()

    def test_create_review_and_access(self):
        url = '/api/artist-reviews/'
        payload = {
            "artist_id": str(self.artist.id),
            "rating": 5,
            "comment": "Great"
        }
        # неавторизованный
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        # авторизованный создаёт
        self.client.force_authenticate(user=self.user)
        res2 = self.client.post(url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        # попытка повторного отзыва -> 400
        res3 = self.client.post(url, payload, format='json')
        self.assertEqual(res3.status_code, status.HTTP_400_BAD_REQUEST)

        # изменение/удаление: только владелец или админ
        review_id = res2.json()['id']
        other = User.objects.create_user(username='other2', password='pass123')
        self.client.force_authenticate(user=other)
        url_detail = f'/api/artist-reviews/{review_id}/'
        res4 = self.client.patch(url_detail, {"rating": 4}, format='json')
        self.assertIn(res4.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        # владелец
        self.client.force_authenticate(user=self.user)
        res5 = self.client.patch(url_detail, {"rating": 4}, format='json')
        self.assertEqual(res5.status_code, status.HTTP_200_OK)


class ArtistAnnotationTests(APITestCase):
    def setUp(self):
        from store.models import ArtistReview
        self.artist = Artist.objects.create(name="ArtAnn", biography="BioAnn")
        self.user1 = User.objects.create_user(username='u1', password='pass')
        self.user2 = User.objects.create_user(username='u2', password='pass')
        ArtistReview.objects.create(artist=self.artist, user=self.user1, rating=4, comment="")
        ArtistReview.objects.create(artist=self.artist, user=self.user2, rating=2, comment="")
        self.client = APIClient()

    def test_artist_list_annotation(self):
        url = '/api/artists/'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        # Если пагинированный ответ: dict с 'results'; иначе список
        if isinstance(body, dict) and 'results' in body:
            data_list = body['results']
        else:
            data_list = body  # ожидаем список
        found = None
        for item in data_list:
            if str(item['id']) == str(self.artist.id):
                found = item
                break
        self.assertIsNotNone(found)
        # средний: (4+2)/2 = 3.0, count=2
        self.assertAlmostEqual(found.get('average_rating'), 3.0)
        self.assertEqual(found.get('reviews_count'), 2)


class PaintingTests(APITestCase):
    def setUp(self):
        self.artist = Artist.objects.create(name="AA", biography="BB")
        self.gallery = Gallery.objects.create(name="GG")
        self.paint1 = Painting.objects.create(
            title="UniqueTitle1", artist=self.artist, gallery=self.gallery,
            price="10.00", status='available'
        )
        self.paint2 = Painting.objects.create(
            title="UniqueTitle2", artist=self.artist, gallery=self.gallery,
            price="20.00", status='available'
        )
        self.client = APIClient()

    def test_unique_title_serializer(self):
        admin = User.objects.create_superuser(username='admin', email='a@a.com', password='pass')
        self.client.force_authenticate(user=admin)
        url = '/api/paintings/'
        payload = {
            "title": "UniqueTitle1",
            "description": "",
            "artist_id": str(self.artist.id),
            "gallery_id": str(self.gallery.id),
            "price": "15.00",
            "status": "available"
        }
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        payload['title'] = "AnotherTitle"
        res2 = self.client.post(url, payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)

    def test_filter_by_date_added(self):
        older = Painting.objects.create(
            title="OldTitle", artist=self.artist, gallery=self.gallery,
            price="30.00", status='available'
        )
        # отодвигаем дату назад
        older.added_at = timezone.now() - datetime.timedelta(days=10)
        older.save()
        # Формируем строку без часового смещения, чтобы избежать 400
        dt = timezone.now() - datetime.timedelta(days=5)
        # Сделаем наивное datetime без tzinfo
        naive = dt.replace(tzinfo=None)
        date_str = naive.isoformat()  # 'YYYY-MM-DDThh:mm:ss'
        url = f'/api/paintings/?added_after={date_str}'
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        body = res.json()
        if isinstance(body, dict) and 'results' in body:
            data_list = body['results']
        else:
            data_list = body
        ids = {item['id'] for item in data_list}
        # Две более новые должны быть, старую нет
        self.assertIn(str(self.paint1.id), ids)
        self.assertIn(str(self.paint2.id), ids)
        self.assertNotIn(str(older.id), ids)