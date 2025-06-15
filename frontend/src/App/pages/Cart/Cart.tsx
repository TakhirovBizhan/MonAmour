// Cart.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import s from './Cart.module.scss';
import Text from '../../../components/Text';
import Card from '../../../components/Card';
import Button from '../../../components/Button';
import Loader from '../../../components/Loader';
import { useGetCartQuery, useDeleteMutation } from '../../../store/api/Cart.api';
import OrderModal, { CartItem } from './Components/OrderModal/OrderModal';

const Cart: React.FC = () => {
  const { data: cartData, isLoading, isError } = useGetCartQuery();
  const [removeFromCart] = useDeleteMutation();
  const [isOrderOpen, setIsOrderOpen] = useState(false);

  if (isLoading) {
    return (
      <div className={s.wrapper}>
        <Text view="title">Ваша корзина</Text>
        <Loader size="l" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className={s.wrapper}>
        <Text view="title">Ваша корзина</Text>
        <Text view="p-18">Ошибка при загрузке корзины.</Text>
      </div>
    );
  }

  const handleRemove = async (cartItemId: string, e: React.MouseEvent) => {
    e.preventDefault();
    try {
      await removeFromCart(cartItemId).unwrap();
    } catch (err) {
      console.error('Ошибка при удалении из корзины', err);
    }
  };

  const openOrderModal = () => setIsOrderOpen(true);
  const closeOrderModal = () => setIsOrderOpen(false);

  const paintings: CartItem[] = cartData?.map((item) => ({ cartItemId: item.id, painting: item.painting })) || [];

  return (
    <div className={s.wrapper}>
      <Text view="title">Ваша корзина</Text>
      <Button onClick={openOrderModal} disabled={!paintings.length} className={s.orderButton}>
        Оформить заказ
      </Button>
      <div className={s.cart_list}>
        {paintings.length > 0 ? (
          paintings.map((item) => (
            <Link key={item.cartItemId} to={`/main/paintings/${item.painting.id}`} className={s.link}>
              <Card
                image={item.painting.images[0]?.image_url}
                captionSlot={item.painting.category.name}
                title={item.painting.title}
                subtitle={item.painting.dimensions}
                contentSlot={`${item.painting.price} р`}
                actionSlot={
                  <Button onClick={(e) => handleRemove(item.cartItemId, e)}>
                    <Text view="button">Удалить из корзины</Text>
                  </Button>
                }
              />
            </Link>
          ))
        ) : (
          <Text view="p-18">Ваша корзина пуста</Text>
        )}
      </div>
      {isOrderOpen && (
        <OrderModal
          isOpen={isOrderOpen}
          onClose={closeOrderModal}
          cartItems={paintings}
          removeFromCart={removeFromCart}
        />
      )}
    </div>
  );
};

export default Cart;
