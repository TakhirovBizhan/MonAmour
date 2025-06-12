import { useGetArtistQuery } from '../../../store/api/authors.api';
import s from './Artist.module.scss';
import Text from '../../../components/Text';

export const Artist = () => {
  const pathname = window.location.pathname;
  const categoryRaw = pathname.includes('artist') ? pathname.split('/').pop() || '' : '';
  const artist = categoryRaw;

  const { data } = useGetArtistQuery(artist);

  return (
    <div className={s.wrapper}>
      <img className={s.artist_img} src={data?.image} alt="аватар автора" />
      <div className={s.text_block}>
        <Text view="title">{data?.name}</Text>
        <Text view="p-18">{data?.biography}</Text>
      </div>
    </div>
  );
};
