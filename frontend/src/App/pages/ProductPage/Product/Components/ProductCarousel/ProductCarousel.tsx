import { memo, useEffect, useState } from 'react';
import cn from 'classnames';
import s from './ProductCarousel.module.scss';
import rightArrowCircle from '../../../../../../../public/rightArrowCircle.svg';
import leftArrowCircle from '../../../../../../../public/leftArrowCircle.svg';
import { useParams } from 'react-router-dom';

interface ProductImageCarouselProps {
  images: string[];
}

const ProductCarousel: React.FC<ProductImageCarouselProps> = ({ images }) => {
  const [currentImage, setCurrentImage] = useState(0);

  const {id} = useParams()
  const handleNextImage = () => {
    setCurrentImage((prev) => (prev < images.length - 1 ? prev + 1 : prev));
  };

  const handlePreviousImage = () => {
    setCurrentImage((prev) => (prev > 0 ? prev - 1 : prev));
  };

  useEffect(() => {
    setCurrentImage(0);
}, [id]);


  return (
    <div className={s.root}>
      <button
        onClick={handleNextImage}
        className={cn(s.root__icon_right, currentImage === images.length - 1 && s.blocked)}
      >
        <img src={rightArrowCircle} alt="Next" />
      </button>
      <img
        className={s.root__image}
        src={images[currentImage].replace(/[[\]"'\\]/g, '')}
        alt="product photo"
      />
      <button
        onClick={handlePreviousImage}
        className={cn(s.root__icon_left, currentImage === 0 && s.blocked)}
      >
        <img src={leftArrowCircle} alt="Previous" />
      </button>
    </div>
  );
};

export default memo(ProductCarousel);