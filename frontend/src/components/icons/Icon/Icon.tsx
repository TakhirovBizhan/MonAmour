import * as React from 'react';
import cn from 'classnames';
import styles from './Icon.module.scss';

export type IconProps = React.SVGAttributes<SVGElement> & {
  className?: string;
  color?: 'primary' | 'secondary' | 'accent';
};

const Icon: React.FC<React.PropsWithChildren<IconProps>> = ({
  className,
  color = 'primary',
  children,
  width = 24,
  height = 24,
  ...props
}) => {
  return (
    <svg
      className={cn(className, styles.icon, color && [styles[`icon_color_${color}`]])}
      xmlns="http://www.w3.org/2000/svg"
      width={width}
      height={height}
      preserveAspectRatio="xMidYMid meet"
      fill="none"
      {...props}
    >
      {children}
    </svg>
  );
};

export default Icon;
