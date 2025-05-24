import React from 'react';
import { Link } from 'react-router-dom';
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { SerializedError } from '@reduxjs/toolkit';
import Button from '../../../../../components/Button';
import Card from '../../../../../components/Card';
import Text from '../../../../../components/Text';
import s from './ProductList.module.scss';
import { IPaintingData } from '../../../../../config/DataInterfaces';

type ProductListProps = {
  data: IPaintingData;
  isLoading: boolean;
  error: FetchBaseQueryError | SerializedError | undefined;
};

export const ProductList: React.FC<ProductListProps> = ({ data, isLoading, error }) => {
  function handleCartAction(...smth: any) {
    console.log(smth);
  }

  return (
    <div className={s.root}>
      {isLoading ? (
        [...Array(9)].map((_, i) => <Card key={i} loading={true} />)
      ) : data ? (
        data.results.map((product) => {
          return (
            <Link key={product.id} to={`/main/paintings/${product.id}`}>
              <Card
                image={product.images[0].image_url}
                captionSlot={product.category.name}
                title={product.title}
                subtitle={product.dimensions}
                contentSlot={`${product.price} p`}
                actionSlot={
                  <Button onClick={(e) => handleCartAction(e, product)}>
                    <Text view="button">{'В корзину'}</Text>
                  </Button>
                }
              />
            </Link>
          );
        })
      ) : error ? (
        <Text view="p-20">Упс... Проблемы с интернетом.</Text>
      ) : null}
    </div>
  );
};

export default ProductList;
