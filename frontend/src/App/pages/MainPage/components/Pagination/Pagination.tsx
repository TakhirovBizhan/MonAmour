import leftArrow from '../../../../../../public/leftArrow.svg';
import rightArrow from '../../../../../../public/rightArrow.svg';
import lightLeftArrow from '../../../../../../public/lightLeftArrow.svg';
import lightRightArrow from '../../../../../../public/lightRightArrow.svg';
import s from './pagination.module.scss';
import ProductList from '../ProductList/ProductList';
import { useDispatch, useSelector } from 'react-redux';
import { decrementPage, incrementPage, setPage } from '../../../../../store/ProductUrlSlice';
import { RootState } from '../../../../../store/index';
import { useGetProductsQuery } from '../../../../../store/api/Products.api';
import Text from '../../../../../components/Text';
import { useTheme } from '../../../../../hooks/useThemes/themeContext';

type PaginationProps = {
  pages: number;
  category?: number;
};

export const Pagination: React.FC<PaginationProps> = ({ pages, category }) => {
  const { page: currentPage, search, rangeFilter } = useSelector((state: RootState) => state.productUrl);
  const { data, isLoading, error } = useGetProductsQuery({ page: currentPage, search, rangeFilter, category });
  const dispatch = useDispatch();

  const { theme } = useTheme();
  const totalPages = Math.ceil(pages / 9);

  const handleNextPage = () => dispatch(incrementPage());
  const handlePreviousPage = () => dispatch(decrementPage());
  const handlePageClick = (newPage: number) => {
    dispatch(setPage(newPage));
  };

  const renderPageButtons = () => {
    let buttons: (number | string)[] = [];
    if (totalPages <= 6) {
      buttons = Array.from({ length: totalPages }, (_, i) => i + 1);
    } else {
      if (currentPage < 3) {
        buttons = [1, 2, 3, '...', totalPages];
      } else if (currentPage >= 3 && currentPage < totalPages - 2) {
        buttons = [1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages];
      } else {
        buttons = [1, '...', totalPages - 2, totalPages - 1, totalPages];
      }
    }
    return buttons;
  };

  return (
    <>
      {data && data.length !== 0 ? (
        <>
          <ProductList data={data} error={error} isLoading={isLoading} />
          <div className={s.pagination}>
            <button onClick={handlePreviousPage} disabled={currentPage === 1}>
              <img src={theme !== 'dark' ? leftArrow : lightLeftArrow} alt="previous page" />
            </button>
            {renderPageButtons().map((btn, index) =>
              btn === '...' ? (
                <span key={index} className={s.ellipsis}>
                  {btn}
                </span>
              ) : (
                <button
                  key={index}
                  className={btn === currentPage ? s.active : ''}
                  onClick={() => handlePageClick(btn as number)}
                >
                  {btn}
                </button>
              ),
            )}
            <button onClick={handleNextPage} disabled={currentPage === totalPages}>
              <img src={theme !== 'dark' ? rightArrow : lightRightArrow} alt="next page" />
            </button>
          </div>
        </>
      ) : !isLoading ? (
        <Text view={'p-20'}>Ops... No data!</Text>
      ) : null}
    </>
  );
};

export default Pagination;
