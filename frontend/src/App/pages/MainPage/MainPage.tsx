// pages/MainPage.tsx (или где у вас находится MainPage)
import Text from '../../../components/Text';
import s from './mainPage.module.scss';
import '../../../styles/styles.scss';
import SearchInput from './components/SearchInput/SearchInput';
import FiltersByGallery from './components/FilterByGallery';
import Pagination from './components/Pagination';
import ProductsCount from './components/ProductsCount';
import { useGetProductsQuery } from '../../../store/api/Products.api';
import { useSelector } from 'react-redux';
import { RootState } from '../../../store';
import FiltersByOrder from './components/filterByOrder';
import { useGetCategoryQuery } from '../../../store/api/Categories.api';
import { useState } from 'react';
import Button from '../../../components/Button';
import AddPaintingModal from './components/AddPaintingModal/addPaintingModal';
import AuthorWidget from './components/Widgets/authorWidget';
import CategoryWidget from './components/Widgets/categoryWidget';
// Импорт для проверки текущего юзера:
import { useGetMeQuery } from '../../../store/api/Auth.api';

const MainPage = () => {
  const pathname = window.location.pathname;
  const categoryRaw = pathname.includes('category') ? pathname.split('/').pop() || '' : '';
  const category = categoryRaw;

  const { data: CategoryData } = useGetCategoryQuery(category);

  const { search, rangeFilter, gallery, sort } = useSelector((state: RootState) => state.productUrl);

  const { data, isLoading } = useGetProductsQuery({ search, rangeFilter, category, gallery, sort });

  const categoryName = categoryRaw ? CategoryData?.name : 'Картины';

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Получаем текущего пользователя
  const { data: me, isLoading: meLoading, isError: meError } = useGetMeQuery();
  // Определяем, админ ли
  const isAdmin = Boolean(me && me.role === 'admin');

  return (
    <main className={s.root}>
      <div className={s.wrapper}>
        {categoryRaw === '' ? (
          <div className={s.widget_block}>
            <Text view="title">Художники</Text>
            <AuthorWidget />

            <Text view="title">Категории</Text>
            <CategoryWidget />
          </div>
        ) : (
          ''
        )}
        <div className={s.root__text_block}>
          <Text view="title">{categoryName}</Text>
          <Text view="p-20">
            Мы отображаем продукцию на основе последних продуктов, которые у нас есть, если вы хотите увидеть наши
            старые продукты, введите название товара.
          </Text>
        </div>
        <div className={s.root__search_block}>
          <SearchInput />
          <div className={s.filters__block}>
            <FiltersByGallery />
            <FiltersByOrder />

            {/* Кнопка + модалка добавления карточки отображаются только для админа */}
            {!meLoading && isAdmin && (
              <>
                <Button onClick={() => setIsModalOpen(true)}>+</Button>
                <AddPaintingModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
              </>
            )}
            {/* Пока meLoading можно ничего не отображать или спиннер, если нужно */}
          </div>
        </div>
        <div className={s.root__pagination_block}>
          {data ? (
            <>
              <ProductsCount dataLength={data.count} loading={isLoading} />
              <Pagination pages={data.count} category={category} />
            </>
          ) : (
            <div>Нет данных...</div>
          )}
        </div>
      </div>
    </main>
  );
};

export default MainPage;
