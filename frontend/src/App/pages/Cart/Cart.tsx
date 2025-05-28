import React from 'react';
import { Link } from 'react-router-dom';
import s from './Cart.module.scss';
import Text from '../../../components/Text';
import Card from '../../../components/Card';
import Button from '../../../components/Button';
import { useGetCartQuery } from '../../../store/api/Cart.api';
import Loader from '../../../components/Loader';

const Cart: React.FC = () => {
  const { data: cartData, isLoading, isError } = useGetCartQuery();

  // Заглушка для действия с корзиной (удалить/добавить и т.д.)
  const handleCartAction = (paintingId: string) => {
    console.log('Cart action for painting id:', paintingId);
    // TODO: здесь ваш код для изменения содержимого корзины
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
          cartData.map((product) => (
            <Link key={product.painting.id} to={`/main/paintings/${product.painting.id}`} className={s.link}>
              <Card
                image={product.painting.images[0].image_url}
                captionSlot={product.painting.category.name}
                title={product.painting.title}
                subtitle={product.painting.dimensions}
                contentSlot={`${product.painting.price} p`}
                actionSlot={
                  <Button onClick={() => handleCartAction(product.painting.id)}>
                    <Text view="button">В корзину</Text>
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
