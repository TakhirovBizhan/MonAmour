import styles from './Text.module.scss';
import cn from 'classnames';
import { memo } from 'react';

export type TextProps = {
  /** Дополнительный класс */
  className?: string;
  /** Стиль отображения */
  view?: 'title' | 'min-title' | 'button' | 'p-20' | 'p-18' | 'p-16' | 'p-14';
  /** Html-тег */
  tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'div' | 'p' | 'span';
  /** Начертание шрифта */
  weight?: 'normal' | 'medium' | 'bold';
  /** Контент */
  children: React.ReactNode;
  /** Цвет */
  color?: 'primary' | 'secondary' | 'accent';
  /** Максимальное кол-во строк */
  maxLines?: number;
};

const Text: React.FC<TextProps> = ({
  className,
  weight = 'normal',
  view = 'p-14',
  tag: Tag = 'p',
  children,
  color = 'primary',
  maxLines,
}) => {
  return (
    <Tag
      className={cn(
        [styles[`text_view_${view}`]],
        weight && [styles[`text_weight_${weight}`]],
        color && [styles[`text_color_${color}`]],
        !!maxLines && styles.text_clamp,
        className,
      )}
      style={{ '--lines-count': maxLines } as React.CSSProperties}
    >
      {children}
    </Tag>
  );
};
export default memo(Text);
