import Button from '../../../../components/Button';
import Text from '../../../../components/Text';
import { Painting } from '../../../../config/DataInterfaces';
import ProductCarousel from './Components/ProductCarousel';
import RelatedProducts from './Components/RelatedProducts';
import s from './Product.module.scss';

export const Product: React.FC<Painting> = (data) => {
  return (
    <>
      <div className={s.product}>
        <ProductCarousel images={data.images.map((image) => image.image_url)}></ProductCarousel>
        <div className={s.product__header}>
          <div className={s.product__header__text}>
            <Text view="title">{data?.title}</Text>
            <Text view="p-20" color="secondary">
              {data?.description}
            </Text>
          </div>
          <div className={s.product__header__purchase}>
            <Text view="title">{data?.price} р</Text>
            <div className={s.product__header__purchase__buttons}>
              <Button>Купить</Button>
              <Button className={s.product__button}>Добавить в корзину</Button>
            </div>
          </div>
        </div>
      </div>
      <div className={s.add_info}>
        <div>
          <Text view="p-20" color="secondary">
            Размер:
          </Text>
          <Text view="p-18" color="accent">
            {data?.dimensions} см
          </Text>
        </div>

        <div>
          <Text view="p-20" color="secondary">
            Техника:
          </Text>
          <Text view="p-18" color="accent">
            {data?.technique}
          </Text>
        </div>

        <div>
          <Text view="p-20" color="secondary">
            Категория:
          </Text>
          <Text view="p-18" color="accent">
            {data?.category.name}
          </Text>
        </div>

        <div>
          <Text view="p-20" color="secondary">
            Галерея:
          </Text>
          <Text view="p-18" color="accent">
            {data?.gallery.name}
          </Text>
        </div>

        <div className={s.author_block}>
          <Text view="p-20" color="secondary">
            Автор:
          </Text>
          <img className={s.author_img} src={data?.artist.image} />
          <Text view="p-18" color="accent">
            {data?.artist.name}
          </Text>
        </div>
      </div>
      <RelatedProducts {...data}></RelatedProducts>
    </>
  );
};

export default Product;
