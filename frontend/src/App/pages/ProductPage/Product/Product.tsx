import Button from '../../../../components/Button';
import Text from '../../../../components/Text';
import { IData } from '../../../../config/DataInterfaces';
import ProductCarousel from './Components/ProductCarousel';
import RelatedProducts from './Components/RelatedProducts';
import s from './Product.module.scss'

export const Product: React.FC<IData> = (data) => {
    return (
        <>
            <div className={s.product}>
                <ProductCarousel images={data.images}></ProductCarousel>
                <div className={s.product__header}>
                    <div className={s.product__header__text}>
                        <Text view='title'>{data?.title}</Text>
                        <Text view="p-20" color="secondary">{data?.description}</Text>
                    </div>
                    <div className={s.product__header__purchase}>
                        <Text view="title">${data?.price}</Text>
                        <div className={s.product__header__purchase__buttons}>
                            <Button>Buy Now</Button>
                            <Button className={s.product__button}>Add to Cart</Button>
                        </div>
                    </div>
                </div>
            </div>
            <RelatedProducts {...data}></RelatedProducts>
        </>
    )
}

export default Product
