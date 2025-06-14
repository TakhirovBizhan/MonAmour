import { Link } from 'react-router-dom';

import Text from '../../../../../components/Text';
import s from './authorWidget.module.scss';
import { useGetArtistsQuery } from '../../../../../store/api/authors.api';
import Loader from '../../../../../components/Loader';
import Card from '../../../../../components/Card';
import Button from '../../../../../components/Button';

export const AuthorWidget = () => {
  const { data, isLoading, error } = useGetArtistsQuery();

  return (
    <div className={s.wrapper}>
      {isLoading ? (
        <Loader size="l" />
      ) : data ? (
        <div className={s.author_list}>
          {data.map((Artist) => (
            <Link key={Artist.id} to={`/artist/${Artist.id}`}>
              <Card
                image={Artist.image}
                className={s.category_card}
                captionSlot={
                  Artist?.average_rating && (
                    <Text view="p-16" color="accent">
                      Рейтинг: {Artist?.average_rating} ⭐
                    </Text>
                  )
                }
                title={Artist.name}
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

export default AuthorWidget;
