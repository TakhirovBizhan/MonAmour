import React from 'react';
import { Link } from 'react-router-dom';
import s from './Cart.module.scss';
import Text from '../../../components/Text';
import Card from '../../../components/Card';
import Button from '../../../components/Button';
import Loader from '../../../components/Loader';
import { useGetCartQuery, useDeleteMutation } from '../../../store/api/Cart.api';

const Cart: React.FC = () => {
  const { data: cartData, isLoading, isError } = useGetCartQuery();
  const [removeFromCart] = useDeleteMutation();

  const handleRemove = async (cartItemId: string, e: React.MouseEvent) => {
    e.preventDefault();
    await removeFromCart(cartItemId);
    // RTK Query invalidates tags and refetches getCart automatically
  };

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

  return (
    <div className={s.wrapper}>
      <Text view="title">Ваша корзина</Text>
      <div className={s.cart_list}>
        {cartData && cartData.length > 0 ? (
          cartData.map((item) => (
            <Link key={item.id} to={`/main/paintings/${item.painting.id}`} className={s.link}>
              <Card
                image={item.painting.images[0].image_url}
                captionSlot={item.painting.category.name}
                title={item.painting.title}
                subtitle={item.painting.dimensions}
                contentSlot={`${item.painting.price} p`}
                actionSlot={
                  <Button onClick={(e) => handleRemove(item.id, e)}>
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
    </div>
  );
};

export default Cart;
