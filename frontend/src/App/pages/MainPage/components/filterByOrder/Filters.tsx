import { useState } from 'react';
import MultiDropdown, { Option } from '../../../../../components/MultiDropdown';
import s from './filters.module.scss';
import { useDispatch } from 'react-redux';
import { setSort } from '../../../../../store/ProductUrlSlice';

export const Filters = () => {
  const [filter, setFilterState] = useState<Option[]>([]);
  const dispatch = useDispatch();

  const handleChange = (value: Option[]) => {
    if (value.length === 0) {
      // Сбросили выбор
      dispatch(setSort(''));
      setFilterState([]);
    } else {
      // Выбрали новую опцию (массив всегда [Option])
      dispatch(setSort(value[0].key));
      setFilterState(value);
    }
  };

  return (
    <MultiDropdown
      className={s.multiDropdown}
      options={[
        { key: 'price_asc', value: 'по возрастанию цены' },
        { key: 'price_desc', value: 'по убыванию цены' },
      ]}
      value={filter}
      onChange={handleChange}
      getTitle={(value) => (value.length > 0 ? value[0].value : 'Порядок')}
    />
  );
};

export default Filters;
