import Loader from '../../../../../components/Loader';
import Text from '../../../../../components/Text';
import s from './ProductsCount.module.scss';

interface TotalProductsProps {
  loading: boolean;
  dataLength: number;
}

export const ProductsCount: React.FC<TotalProductsProps> = ({ loading, dataLength }) => {
  return (
    <>
      {loading ? (
        <Loader size="l" />
      ) : (
        <div className={s.text_block}>
          <Text view="min-title" weight="bold">
            Total Product
          </Text>
          <Text view="p-20" color="accent">
            {dataLength}
          </Text>
        </div>
      )}
    </>
  );
};

export default ProductsCount;
