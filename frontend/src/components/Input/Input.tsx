import React, { memo, useCallback } from 'react';  
import cn from 'classnames'; 
import styles from './Input.module.scss'; 
export type InputProps = Omit< 
  React.InputHTMLAttributes<HTMLInputElement>, 
  'onChange' | 'value' 
> & { 
  /** Значение поля */ 
  value: string; 
  /** Callback, вызываемый при вводе данных в поле */ 
  onChange: (value: string) => void; 
  /** Слот для иконки справа */ 
  afterSlot?: React.ReactNode; 
}; 
 
const Input = React.forwardRef<HTMLInputElement, InputProps>( 
  ({ afterSlot, value, onChange, className, disabled, ...props }, ref) => { 
    const handleOnChange = useCallback( 
      (event: React.ChangeEvent<HTMLInputElement>): void => { 
        onChange(event.target.value); 
      }, 
      [onChange]  
    ); 
 
    return ( 
      <label className={cn(className, styles.input, disabled && styles.input_disabled)}> 
        <input 
        className={styles.input__field}
          type='text' 
          value={value} 
          disabled={disabled} 
          onChange={handleOnChange} 
          ref={ref} 
          {...props} 
        /> 
        {afterSlot && <div className={styles.input__after}>{afterSlot}</div>} 
      </label> 
    ); 
  } 
); 
export default memo(Input);
