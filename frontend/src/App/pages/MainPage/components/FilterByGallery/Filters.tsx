import { useEffect, useState } from 'react';
import MultiDropdown, { Option } from '../../../../../components/MultiDropdown';
import s from './filters.module.scss';
import axios from 'axios';
import { useDispatch } from 'react-redux';
import { setGallery } from '../../../../../store/ProductUrlSlice';

export const Filters = () => {
  const [filter, setFilterState] = useState<Option[]>([]);
  const [filterData, setFilterData] = useState<Option[]>([]);
  const dispatch = useDispatch();

  const handleChange = (value: Option[]) => {
    if (value.length === 0) {
      // Сбросили выбор
      dispatch(setGallery(''));
      setFilterState([]);
    } else {
      // Выбрали новую опцию (массив всегда [Option])
      dispatch(setGallery(value[0].key));
      setFilterState(value);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await axios.get('http://localhost:8000/api/galleries/id-name/');
        setFilterData(
          result.data.map((item: { id: string; name: string }) => ({
            key: item.id,
            value: item.name,
          })),
        );
      } catch (error) {
        console.error(error);
      }
    };

    fetchData();
  }, []);

  return (
    <MultiDropdown
      className={s.multiDropdown}
      options={filterData}
      value={filter}
      onChange={handleChange}
      getTitle={(value) => (value.length > 0 ? value[0].value : 'Галерея')}
    />
  );
};

export default Filters;
