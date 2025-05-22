import s from './Cart.module.scss';
import Text from '../../../components/Text';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store/index';
import ProductList from '../MainPage/components/ProductList/ProductList';

const Cart = () => {
  const { data, fullPrice } = useSelector((state: RootState) => state.cart);
  return (
    <div className={s.wrapper}>
      <Text view="title">Your cart</Text>
      <Text className={s.price} color="accent" view="p-20">
        Price of cart: ${fullPrice}
      </Text>
      <ProductList data={data} isLoading={false} error={undefined} />
    </div>
  );
};
export default Cart;
