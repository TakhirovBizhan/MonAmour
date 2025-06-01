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
  const setFilterStateFull = (Option: Option[]) => {
    dispatch(setGallery(Option[0].key));
    setFilterState(Option);
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
      onChange={(value: Option[]) => {
        setFilterStateFull(value);
      }}
      getTitle={() => (filter.length ? filter.map((el) => el.value).join(', ') : 'Галерея')}
    />
  );
};

export default Filters;
