import { Link } from 'react-router-dom';
import Button from '../../../../../../components/Button';
import Text from '../../../../../../components/Text';
import Card from '../../../../../../components/Card';
import { IData } from '../../../../../../config/DataInterfaces';
import { useProducts } from '../../../../../../api/api';
import Loader from '../../../../../../components/Loader';
import s from './RelatedProducts.module.scss';
import { memo } from 'react';

export const RelatedProducts = (product: IData) => {
  const { data, loading } = useProducts();

  return (
    <>
      {loading ? (
        <Loader className={s.loader} size="l" />
      ) : (
        <div className={s.root}>
          <Text className={s.root__title} view="title">
            Related Items
          </Text>
          <div className={s.root__list}>
            {data
              .filter((el) => el.category.name === product?.category.name)
              .slice(0, 3)
              .map((el) => (
                <Link key={el.id} to={`/main/product/${el.id}`}>
                  <Card
                    image={el.images[0]}
                    captionSlot={el.category.name}
                    title={el.title}
                    subtitle={el.description}
                    contentSlot={`$${el.price}`}
                    actionSlot={
                      <Button>
                        <Text view="button">Add to Cart</Text>
                      </Button>
                    }
                  />
                </Link>
              ))}
          </div>
        </div>
      )}
    </>
  );
};

export default memo(RelatedProducts);
