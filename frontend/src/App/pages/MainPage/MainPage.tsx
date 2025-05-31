import Text from '../../../components/Text';
import s from './mainPage.module.scss';
import '../../../styles/styles.scss';
import SearchInput from './components/SearchInput/SearchInput';
import Filters from './components/Filters';
import Pagination from './components/Pagination';
import ProductsCount from './components/ProductsCount';
import { useGetProductsQuery } from '../../../store/api/Products.api';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store';
import Loader from '../../../components/Loader';
import { useGetCategoryQuery } from '../../../store/api/Categories.api';

const MainPage: React.FC = () => {
  const pathname = window.location.pathname;
  const categoryRaw = pathname.includes('category') ? pathname.split('/').pop() || '' : '';
  const category = categoryRaw;

  const { data: categoryData, isLoading: categoryLoading } = useGetCategoryQuery(category, { skip: !category });

  const { search, rangeFilter } = useSelector((state: RootState) => state.productUrl);

  const { data, isLoading } = useGetProductsQuery({ search, rangeFilter, category });

  const categoryName = categoryRaw ? (categoryData?.name ?? 'Картины') : 'Картины';

  return (
    <main className={s.root}>
      <div className={s.wrapper}>
        <div className={s.root__text_block}>
          {category && categoryLoading ? <Loader size="s" /> : <Text view="title">{categoryName}</Text>}
          <Text view="p-20">
            Мы отображаем продукцию на основе последних продуктов, которые у нас есть, если вы хотите увидеть наши
            старые продукты, введите название товара.
          </Text>
        </div>
        <div className={s.root__search_block}>
          <SearchInput />
          <Filters />
        </div>
        <div className={s.root__pagination_block}>
          {data ? (
            <>
              <ProductsCount dataLength={data.count} loading={isLoading} />
              <Pagination pages={data.count} category={category} />
            </>
          ) : null}
        </div>
      </div>
    </main>
  );
};

export default MainPage;
