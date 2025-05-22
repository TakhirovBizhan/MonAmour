import styles from './Button.module.scss';
import Loader from '../Loader';
import Text from '../Text';
import cn from 'classnames';
import { memo } from 'react';

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  /** Состояние загрузки */
  loading?: boolean;
  /** Текст кнопки */
  children: React.ReactNode;
};


const Button: React.FC<ButtonProps> = (
  {className,
    loading,
    disabled,
    children,
    ...props
  }
) => {
  return (
    <button
    className={cn(className, styles.button, disabled && styles.button_disabled)}
    disabled={disabled || loading}
    {...props}
    >
      {loading && <Loader className={styles.button__loader} size='s' />}
      <Text tag='span' view="button">
        {children}
      </Text>
    </button>
  )
}

export default memo(Button);
