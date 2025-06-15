import { useGetArtistQuery, useGetReviewsByArtistQuery } from '../../../store/api/authors.api';
import s from './Artist.module.scss';
import Text from '../../../components/Text';
import Loader from '../../../components/Loader';

export const Artist = () => {
  const pathname = window.location.pathname;
  const categoryRaw = pathname.includes('artist') ? pathname.split('/').pop() || '' : '';
  const artist = categoryRaw;

  const { data } = useGetArtistQuery(artist);
  const { data: reviewData, isLoading } = useGetReviewsByArtistQuery(artist);

  return (
    <div className={s.wrapper}>
      <img className={s.artist_img} src={data?.image} alt="аватар автора" />
      <div className={s.text_block}>
        <Text view="title">{data?.name}</Text>
        <Text view="p-18">{data?.biography}</Text>
        {data?.average_rating && (
          <Text view="p-16" color="accent">
            Рейтинг: {data.average_rating} ⭐
          </Text>
        )}
      </div>

      {isLoading ? (
        <Loader size="l" />
      ) : reviewData && reviewData.length > 0 ? (
        <div className={s.review_block}>
          <Text view="title">Отзывы</Text>
          {reviewData.map((review, index) => (
            <div key={index} className={s.review_item}>
              <Text view="p-18">Имя пользователя: {review.user}</Text>
              <Text view="p-18" color="accent">
                Оценка: {review.rating} ⭐
              </Text>
              {review.comment && (
                <>
                  <Text view="p-16">Отзыв</Text>
                  <Text view="p-16" color="secondary">
                    {review.comment}
                  </Text>
                </>
              )}
            </div>
          ))}
        </div>
      ) : (
        <Text view="p-16">Пока нет отзывов.</Text>
      )}
    </div>
  );
};
