import React, { memo } from 'react';
import cn from 'classnames';
import styles from './MultiDropdown.module.scss';
import Input from '../Input';
import Text from '../Text';
import ArrowDownIcon from '../icons/ArrowDownIcon';

export type Option = {
  /** Ключ варианта, используется для отправки на бек/использования в коде */
  key: string;
  /** Значение варианта, отображается пользователю */
  value: string;
};

/** Пропсы, которые принимает компонент Dropdown */
export type MultiDropdownProps = {
  className?: string;
  /** Массив возможных вариантов для выбора */
  options: Option[];
  /** Текущие выбранные значения поля, может быть пустым */
  value: Option[];
  /** Callback, вызываемый при выборе варианта */
  onChange: (value: Option[]) => void;
  /** Заблокирован ли дропдаун */
  disabled?: boolean;
  /** Возвращает строку которая будет выводится в инпуте. В случае если опции не выбраны, строка должна отображаться как placeholder. */
  getTitle: (value: Option[]) => string;
};

const MultiDropdown: React.FC<MultiDropdownProps> = ({ className, options, value, onChange, disabled, getTitle }) => {
  const wrapperRef = React.useRef<HTMLDivElement>(null);
  const ref = React.useRef<HTMLInputElement>(null);
  const [filter, setFilter] = React.useState('');
  const [isOpened, setIsOpened] = React.useState(false);
  const open = () => {
    setIsOpened(true);
  };
  React.useEffect(() => {
    const handlerClick = (e: MouseEvent) => {
      if (!wrapperRef.current?.contains(e.target as HTMLElement)) {
        setIsOpened(false);
      }
    };
    window.addEventListener('click', handlerClick);
    return () => {
      window.removeEventListener('click', handlerClick);
    };
  }, []);
  React.useEffect(() => {
    if (!isOpened) {
      setFilter('');
    }
  }, [isOpened]);
  const title = React.useMemo(() => getTitle(value), [getTitle, value]);

  const isEmpty = value.length === 0;

  const filteredOptions = React.useMemo(() => {
    const str = filter.toLocaleLowerCase();

    return options.filter((o) => o.value.toLocaleLowerCase().indexOf(str) === 0);
  }, [filter, options]);

  const selectedKeysSet = React.useMemo<Set<Option['key']>>(() => new Set(value.map(({ key }) => key)), [value]);

  const onSelect = React.useCallback(
    (option: Option) => {
      if (disabled) {
        return;
      }

      if (selectedKeysSet.has(option.key)) {
        onChange([...value].filter(({ key }) => key !== option.key));
      } else {
        onChange([...value, option]);
      }

      ref.current?.focus();
    },
    [disabled, onChange, value, selectedKeysSet],
  );
  const opened = isOpened && !disabled;
  return (
    <div className={cn(className, styles.multi_dropdown)} ref={wrapperRef}>
      <Input
        className={styles.multi_dropdown__field}
        onClick={open}
        disabled={disabled}
        placeholder={title}
        value={opened ? filter : isEmpty ? '' : title}
        onChange={setFilter}
        afterSlot={<ArrowDownIcon color="secondary" />}
        ref={ref}
      />
      {opened && (
        <div className={styles.multi_dropdown__options}>
          {filteredOptions.map((option) => (
            <button
              className={cn(
                styles.multi_dropdown__option,
                selectedKeysSet.has(option.key) && styles.multi_dropdown__option_selected,
              )}
              key={option.key}
              onClick={() => {
                onSelect(option);
              }}
            >
              <Text view="p-16">{option.value}</Text>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default memo(MultiDropdown);
