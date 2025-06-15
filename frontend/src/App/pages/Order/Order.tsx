import React from 'react';
import Text from '../../../components/Text';
import Loader from '../../../components/Loader';
import s from './Order.module.scss';
import { useGetOrderByIdQuery } from '../../../store/api/Orders.api';
import { orderItem } from '../../../config/DataInterfaces';

const Order: React.FC = () => {
  const pathname = window.location.pathname;
  const orderId = pathname.includes('order') ? pathname.split('/').pop() || '' : '';
  const { data: order, isLoading, isError, error } = useGetOrderByIdQuery(orderId!);

  if (isLoading) {
    return (
      <div className={s.wrapper}>
        <Text view="title">Загрузка заказа...</Text>
        <Loader size="l" />
      </div>
    );
  }
  if (isError || !order) {
    console.log(error);
    return (
      <div className={s.wrapper}>
        <Text view="title">Ошибка загрузки заказа</Text>
      </div>
    );
  }

  const formatDate = (iso: string) => {
    try {
      const date = new Date(iso);
      return date.toLocaleString();
    } catch {
      return iso;
    }
  };

  return (
    <div className={s.wrapper}>
      <Text view="title">Заказ #{order.id}</Text>
      <div className={s.section}>
        <Text view="p-18" color="secondary">
          Дата: {formatDate(order.order_date)}
        </Text>
        <Text view="p-18" color="secondary">
          Статус: {order.status}
        </Text>
      </div>
      <div className={s.section}>
        <Text view="min-title">Адрес доставки</Text>
        <div className={s.address}>
          <Text view="p-18">Улица: {order.street}</Text>
          <Text view="p-18">Дом: {order.house_number}</Text>
          <Text view="p-18">Город: {order.city}</Text>
          <Text view="p-18">Почтовый индекс: {order.postal_code}</Text>
          {order.address_comment && <Text view="p-18">Комментарий: {order.address_comment}</Text>}
        </div>
      </div>
      <div className={s.section}>
        <Text view="min-title">Оплата и контакт</Text>
        <Text view="p-18">Способ оплаты: {order.payment_method === 'card' ? 'Картой' : 'Наличными'}</Text>
        <Text view="p-18">Телефон: {order.phone_number || '-'}</Text>
        <Text view="p-18">Пользователь: {order.user}</Text>
      </div>
      <div className={s.section}>
        <Text view="min-title">Картины в заказе</Text>
        <ul className={s.itemsList}>
          {order.items.map((item) => (
            <OrderItemRow key={item.id} item={item} />
          ))}
        </ul>
      </div>
    </div>
  );
};

interface OrderItemProps {
  item: orderItem;
}

const OrderItemRow: React.FC<OrderItemProps> = ({ item }) => {
  const painting = item.painting;
  // Отображаем данные из nested painting
  const imageUrl = painting.images && painting.images.length > 0 ? painting.images[0].image_url : '';
  return (
    <li className={s.itemRow}>
      {imageUrl ? (
        <img src={imageUrl} alt={painting.title} className={s.itemImage} />
      ) : (
        <div className={s.noImage}>Нет изображения</div>
      )}
      <div className={s.itemInfo}>
        <Text view="p-18">{painting.title}</Text>
        <Text view="p-16" color="secondary">
          Цена на момент заказа: {item.price_at_purchase} р
        </Text>
        <Text view="p-14" color="secondary">
          Заказано: {new Date(item.purchased_at).toLocaleString()}
        </Text>
      </div>
    </li>
  );
};

export default Order;
