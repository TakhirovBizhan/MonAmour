import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { SerializedError } from '@reduxjs/toolkit';
import Button from '../../../../../components/Button';
import Card from '../../../../../components/Card';
import Text from '../../../../../components/Text';
import s from './ProductList.module.scss';
import { IData } from '../../../../../config/DataInterfaces';
import { addToCart, removeFromCart } from '../../../../../store/CartSlice';
import { RootState } from '../../../../../store';

type ProductListProps = {
  data: IData[];
  isLoading: boolean;
  error: FetchBaseQueryError | SerializedError | undefined;
};

export const ProductList: React.FC<ProductListProps> = ({ data, isLoading, error }) => {
  const dispatch = useDispatch();
  const cartItems = useSelector((state: RootState) => state.cart.data);

  const handleCartAction = (e: React.MouseEvent, product: IData, inCart: boolean) => {
    e.preventDefault();
    if (inCart) {
      dispatch(removeFromCart(product.id));
    } else {
      dispatch(addToCart(product));
    }
  };

  return (
    <div className={s.root}>
      {isLoading ? (
        [...Array(9)].map((_, i) => <Card key={i} loading={true} />)
      ) : data ? (
        data.map((product) => {
          // Проверяем, есть ли товар в корзине по id
          const inCart = cartItems.some((item: IData) => item.id === product.id);

          return (
            <Link key={product.id} to={`/main/product/${product.id}`}>
              <Card
                image={product.images[0].replace(/[[\]"'\\]/g, '')}
                captionSlot={product.category.name}
                title={product.title}
                subtitle={product.description}
                contentSlot={`$${product.price}`}
                actionSlot={
                  <Button onClick={(e) => handleCartAction(e, product, inCart)}>
                    <Text view="button">{inCart ? 'Remove from Cart' : 'Add to Cart'}</Text>
                  </Button>
                }
              />
            </Link>
          );
        })
      ) : error ? (
        <Text view="p-20">Ooops... Some network errors.</Text>
      ) : null}
    </div>
  );
};

export default ProductList;
