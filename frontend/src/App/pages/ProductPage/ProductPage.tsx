import { useNavigate, useParams } from 'react-router-dom';
import { useProduct } from '../../../api/api';
import Loader from '../../../components/Loader';
import s from './ProductPage.module.scss';
import Text from '../../../components/Text';
import leftArrow from '../../../../public/leftArrow.svg';
import Product from './Product/Product';

export const ProductPage = () => {
  const { id } = useParams();
  const { data, loading } = useProduct(id);
  const navigate = useNavigate();

  return (
    <div className={s.wrapper}>
      <button className={s.go_back} onClick={() => navigate(-1)}>
        <img src={leftArrow} alt="previous page" />
        <Text view="p-20">Назад</Text>
      </button>
      {loading ? <Loader className={s.loader} size="l" /> : <div>{data && <Product {...data} />}</div>}
    </div>
  );
};

export default ProductPage;
