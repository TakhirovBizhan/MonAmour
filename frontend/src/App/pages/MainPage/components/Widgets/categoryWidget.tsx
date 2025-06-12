import { Link } from 'react-router-dom';

import Text from '../../../../../components/Text';
import s from './authorWidget.module.scss';
import Loader from '../../../../../components/Loader';
import Card from '../../../../../components/Card';
import Button from '../../../../../components/Button';
import { useGetCategoriesQuery } from '../../../../../store/api/Categories.api';

export const CategoryWidget = () => {
  const { data, isLoading, error } = useGetCategoriesQuery();

  return (
    <div className={s.wrapper}>
      {isLoading ? (
        <Loader size="l" />
      ) : data ? (
        <div className={s.author_list}>
          {data.map((category) => (
            <Link key={category.id} to={`/category/${category.id}`}>
              <Card
                className={s.category_card}
                title={category.name}
                subtitle={category.description}
                actionSlot={
                  <Button className={s.action_btn}>
                    <Text view="button">посмотреть</Text>
                  </Button>
                }
              />
            </Link>
          ))}
        </div>
      ) : error ? (
        <Text view="p-20">Данных нет, ошибка...</Text>
      ) : null}
    </div>
  );
};

export default CategoryWidget;
