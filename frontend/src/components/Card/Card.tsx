import cn from 'classnames';
import styles from './Card.module.scss';
import Text from '../Text';
import { memo } from 'react';
import { Skeleton } from '../Skeleton/Skeleton';
export type CardProps = {
  /** Дополнительный classname */
  className?: string;
  /** URL изображения */
  image?: string;
  /** Слот над заголовком */
  captionSlot?: React.ReactNode;
  /** Заголовок карточки */
  title?: React.ReactNode;
  /** Описание карточки */
  subtitle?: React.ReactNode;
  /** Содержимое карточки (футер/боковая часть), может быть пустым */
  contentSlot?: React.ReactNode;
  /** Клик на карточку */
  onClick?: React.MouseEventHandler;
  /** Слот для действия */
  actionSlot?: React.ReactNode;
  loading?: boolean;
};

const Card: React.FC<CardProps> = ({
  className,
  image,
  captionSlot,
  title,
  subtitle,
  contentSlot,
  actionSlot,
  onClick,
  loading,
}) => {
  return (
    <>
      {loading ? (
        <div className={styles.card}>
          <Skeleton />
        </div>
      ) : (
        <div className={cn(className, styles.card)} onClick={onClick}>
          <div className={styles.card__header}>
            <img className={styles.card__image} src={image} alt="card" />
          </div>
          <div className={styles.card__body}>
            {captionSlot && (
              <Text className={styles.card__caption} view="p-14" weight="medium" color="secondary">
                {captionSlot}
              </Text>
            )}
            <Text tag="h4" view="p-20" weight="medium" color="primary" maxLines={2}>
              {title}
            </Text>
            <Text className={styles.card__subtitle} view="p-16" color="secondary" maxLines={3}>
              {subtitle}
            </Text>
            <div className={styles.card__footer}>
              {contentSlot && (
                <Text className={styles.card__content} view="p-18" weight="bold" color="primary">
                  {contentSlot}
                </Text>
              )}
              <div className={styles.card__action}>{actionSlot}</div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default memo(Card);
