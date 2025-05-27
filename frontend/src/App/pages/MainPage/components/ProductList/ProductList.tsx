// components/ProductList/ProductList.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { SerializedError } from '@reduxjs/toolkit';
import Button from '../../../../../components/Button';
import Card from '../../../../../components/Card';
import Text from '../../../../../components/Text';
import s from './ProductList.module.scss';
import { IPaintingData } from '../../../../../config/DataInterfaces';
import { useAddMutation, useDeleteMutation, useGetCartQuery } from '../../../../../store/api/Cart.api';

type ProductListProps = {
  data: IPaintingData;
  isLoading: boolean;
  error: FetchBaseQueryError | SerializedError | undefined;
};

export const ProductList: React.FC<ProductListProps> = ({ data, isLoading, error }) => {
  const user_id = localStorage.getItem('currentUser')!;
  // 1) Получаем корзину
  const { data: cartData, isFetching: cartLoading } = useGetCartQuery();
  // 2) Мутации добавления и удаления
  const [addToCart] = useAddMutation();
  const [removeFromCart] = useDeleteMutation();

  // 3) Собираем Set из id в корзине
  const cartSet = React.useMemo(() => {
    if (!cartData) return new Set<string>();
    return new Set(cartData.map((item) => item.painting.id));
  }, [cartData]);

  const handleCartAction = async (paintingId: string, inCart: boolean) => {
    if (inCart) {
      await removeFromCart(paintingId);
    } else {
      await addToCart({ user: user_id, painting_id: paintingId });
    }
    // Можно здесь рефетчить корзину автоматически или RTK Query сделает это за вас
  };

  if (isLoading || cartLoading) {
    return (
      <div className={s.root}>
        {[...Array(9)].map((_, i) => (
          <Card key={i} loading />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={s.root}>
        <Text view="p-20">Упс... Проблемы с интернетом.</Text>
      </div>
    );
  }

  return (
    <div className={s.root}>
      {data?.results.map((product) => {
        const inCart = cartSet.has(product.id);
        return (
          <Link key={product.id} to={`/main/paintings/${product.id}`} className={s.link}>
            <Card
              image={product.images[0].image_url}
              captionSlot={product.category.name}
              title={product.title}
              subtitle={product.dimensions}
              contentSlot={`${product.price} p`}
              actionSlot={
                <Button
                  onClick={(e) => {
                    e.preventDefault();
                    handleCartAction(product.id, inCart);
                  }}
                >
                  <Text view="button">{inCart ? 'Удалить из корзины' : 'Добавить в корзину'}</Text>
                </Button>
              }
            />
          </Link>
        );
      })}
    </div>
  );
};

export default ProductList;
