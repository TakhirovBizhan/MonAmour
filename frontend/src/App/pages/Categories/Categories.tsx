import { Link } from 'react-router-dom';
import Button from '../../../components/Button';
import Card from '../../../components/Card';
import Loader from '../../../components/Loader';
import Text from '../../../components/Text';
import { useGetCategoriesQuery } from '../../../store/api/Categories.api';
import s from './Categories.module.scss';
import cn from 'classnames';

type categoryProps = {
  className?: string;
};

export const Categories: React.FC<categoryProps> = ({ className }) => {
  const { data, isLoading, error } = useGetCategoriesQuery();

  return (
    <main>
      <div className={s.wrapper}>
        {isLoading ? (
          <Loader size="l" />
        ) : data ? (
          <div className={cn(s.category_list, className)}>
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
    </main>
  );
};

export default Categories;
