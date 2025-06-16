// src/pages/Artist/Artist.tsx
import React, { useState } from 'react';
import {
  useGetArtistQuery,
  useGetReviewsByArtistQuery,
  useCreateArtistReviewMutation,
} from '../../../store/api/authors.api';
import s from './Artist.module.scss';
import Text from '../../../components/Text';
import Loader from '../../../components/Loader';
import Button from '../../../components/Button';
import { useAuth } from '../../../hooks/useAuth/useAuth';

export const Artist: React.FC = () => {
  // Предполагаем, что route настроен как /artist/:artistId
  const pathname = window.location.pathname;
  const artistRaw = pathname.includes('artist') ? pathname.split('/').pop() || '' : '';

  const id = artistRaw || '';

  const { data: artist, isLoading: loadingArtist, isError: errorArtist } = useGetArtistQuery(id);
  const {
    data: reviewData,
    isLoading: loadingReviews,
    isError: errorReviews,
    refetch: refetchReviews,
  } = useGetReviewsByArtistQuery(id, {
    // опционально: skip: !id
  });

  const [createReview, { isLoading: isCreatingReview }] = useCreateArtistReviewMutation();
  const { isAuthenticated } = useAuth();

  const [isModalOpen, setModalOpen] = useState(false);
  const [rating, setRating] = useState<number>(5);
  const [comment, setComment] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (loadingArtist) {
    return (
      <div className={s.wrapper}>
        <Loader size="l" />
      </div>
    );
  }
  if (errorArtist || !artist) {
    return (
      <div className={s.wrapper}>
        <Text view="title">Ошибка загрузки автора</Text>
      </div>
    );
  }

  const openModal = () => {
    if (!isAuthenticated) {
      // Можно перенаправить на логин или показать сообщение
      alert('Пожалуйста, войдите, чтобы оставить отзыв.');
      return;
    }
    setRating(5);
    setComment('');
    setErrorMsg(null);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    // Валидация: rating 1-5
    if (rating < 1 || rating > 5) {
      setErrorMsg('Оценка должна быть от 1 до 5.');
      return;
    }
    try {
      await createReview({ artist_id: id, rating, comment: comment.trim() || undefined }).unwrap();
      // После успешного создания:
      refetchReviews();
      closeModal();
    } catch (err: any) {
      console.error('Ошибка при отправке отзыва:', err);
      // Показываем краткое сообщение
      if (err?.data && typeof err.data === 'object') {
        const detail = (err.data as any).detail || JSON.stringify(err.data);
        setErrorMsg(`Ошибка: ${detail}`);
      } else {
        setErrorMsg('Ошибка при отправке отзыва.');
      }
    }
  };

  return (
    <div className={s.wrapper}>
      <div className={s.header}>
        <img className={s.artist_img} src={artist.image} alt="аватар автора" />
        <div className={s.text_block}>
          <Text view="title">{artist.name}</Text>
          <Text view="p-18">{artist.biography}</Text>
          {artist.average_rating !== null && (
            <Text view="p-16" color="accent">
              Рейтинг: {artist.average_rating} ⭐ ({artist.reviews_count})
            </Text>
          )}
        </div>
      </div>

      <div className={s.actionsRow}>
        <Button onClick={openModal} disabled={!isAuthenticated}>
          Написать отзыв
        </Button>
      </div>

      {/* Список отзывов */}
      <div className={s.review_block}>
        <Text view="title">Отзывы</Text>
        {loadingReviews ? (
          <Loader size="l" />
        ) : errorReviews ? (
          <Text view="p-18">Ошибка загрузки отзывов.</Text>
        ) : reviewData && reviewData.length > 0 ? (
          reviewData.map((review) => (
            <div key={review.id} className={s.review_item}>
              <Text view="p-18">Пользователь: {review.user}</Text>
              <Text view="p-18" color="accent">
                Оценка: {review.rating} ⭐
              </Text>
              {review.comment && (
                <>
                  <Text view="p-16">Комментарий:</Text>
                  <Text view="p-16" color="secondary">
                    {review.comment}
                  </Text>
                </>
              )}
              <Text view="p-14" color="secondary">
                {new Date(review.created_at).toLocaleString()}
              </Text>
            </div>
          ))
        ) : (
          <Text view="p-16">Пока нет отзывов.</Text>
        )}
      </div>

      {/* Модальное окно для создания/редактирования отзыва */}
      {isModalOpen && (
        <div className={s.modalOverlay} onClick={closeModal}>
          <div className={s.modal} onClick={(e) => e.stopPropagation()}>
            <button className={s.closeBtn} onClick={closeModal}>
              &times;
            </button>
            <Text view="title">Оставить отзыв</Text>
            <form className={s.form} onSubmit={handleSubmit} noValidate>
              <div className={s.field}>
                <label>
                  <Text view="p-18">Оценка*</Text>
                  <select value={rating} onChange={(e) => setRating(Number(e.target.value))} required>
                    {[5, 4, 3, 2, 1].map((val) => (
                      <option key={val} value={val}>
                        {val} ⭐
                      </option>
                    ))}
                  </select>
                </label>
              </div>
              <div className={s.field}>
                <label>
                  <Text view="p-18">Комментарий</Text>
                  <textarea value={comment} onChange={(e) => setComment(e.target.value)} rows={4} />
                </label>
              </div>
              {errorMsg && (
                <div className={s.errorMsg}>
                  <Text view="p-14">{errorMsg}</Text>
                </div>
              )}
              <div className={s.actions}>
                <Button type="submit" disabled={isCreatingReview}>
                  {isCreatingReview ? 'Отправка...' : 'Отправить'}
                </Button>
                <Button onClick={closeModal} type="button" className={s.cancelBtn}>
                  Отмена
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Artist;
