import Text from '../../../components/Text';
import s from './mainPage.module.scss';
import '../../../styles/styles.scss';
import SearchInput from './components/SearchInput/SearchInput';
import Filters from './components/Filters';
import Pagination from './components/Pagination';
import ProductsCount from './components/ProductsCount';
import { useGetAllProductsQuery } from '../../../store/api/Products.api';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store';
import Loader from '../../../components/Loader';
import { useGetCategoryQuery } from '../../../store/api/Categories.api';

const MainPage: React.FC = () => {
  const pathname = window.location.pathname;
  const categoryRaw = pathname.includes('category') ? pathname.split('/').pop() || '' : '';
  const category = categoryRaw && !isNaN(Number(categoryRaw)) ? Number(categoryRaw) : undefined;

  const { data: categoryData, isLoading: categoryLoading } = useGetCategoryQuery(category, { skip: !category });

  const { search, rangeFilter } = useSelector((state: RootState) => state.productUrl);

  const { data, isLoading } = useGetAllProductsQuery({ search, rangeFilter, category });

  const categoryName = categoryRaw ? (categoryData?.name ?? 'Products') : 'Products';

  return (
    <main className={s.root}>
      <div className={s.wrapper}>
        <div className={s.root__text_block}>
          {category && categoryLoading ? <Loader size="s" /> : <Text view="title">{categoryName}</Text>}
          <Text view="p-20">
            We display products based on the latest products we have, if you want to see our old products please enter
            the name of the item
          </Text>
        </div>
        <div className={s.root__search_block}>
          <SearchInput />
          <Filters />
        </div>
        <div className={s.root__pagination_block}>
          {data ? (
            <>
              <ProductsCount dataLength={data.length} loading={isLoading} />
              <Pagination pages={data.length} category={category} />
            </>
          ) : null}
        </div>
      </div>
    </main>
  );
};

export default MainPage;
