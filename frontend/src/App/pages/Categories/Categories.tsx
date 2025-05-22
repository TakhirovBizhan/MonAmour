import { Link } from 'react-router-dom';
import Button from '../../../components/Button';
import Card from '../../../components/Card';
import Loader from '../../../components/Loader';
import Text from '../../../components/Text';
import { useGetCategoriesQuery } from '../../../store/api/Categories.api';
import s from './Categories.module.scss';

export const Categories = () => {
  const { data, isLoading, error } = useGetCategoriesQuery();

  return (
    <main>
      <div className={s.wrapper}>
        {isLoading ? (
          <Loader size="l" />
        ) : data ? (
          <div className={s.category_list}>
            {data.map((category) => (
              <Link key={category.id} to={`/category/${category.id}`}>
                <Card
                  className={s.category_card}
                  title={category.name}
                  image={category.image}
                  actionSlot={
                    <Button className={s.action_btn}>
                      <Text view="button">See</Text>
                    </Button>
                  }
                />
              </Link>
            ))}
          </div>
        ) : error ? (
          <Text view="p-20">ooops.. Some error, we already trying to fix up.</Text>
        ) : null}
      </div>
    </main>
  );
};

export default Categories;
