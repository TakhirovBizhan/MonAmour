// components/ProductList/ProductList.tsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { SerializedError } from '@reduxjs/toolkit';
import Button from '../../../../../components/Button';
import Card from '../../../../../components/Card';
import Text from '../../../../../components/Text';
import s from './ProductList.module.scss';
import { IPaintingData, Painting } from '../../../../../config/DataInterfaces'; // убедитесь, что импортируете Painting
import { useAddMutation, useDeleteMutation, useGetCartQuery } from '../../../../../store/api/Cart.api';
import { useDeletePaintingMutation } from '../../../../../store/api/Products.api';
import EditPaintingModal from '../AddPaintingModal/redactPaintingModal';

type ProductListProps = {
  data: IPaintingData;
  isLoading: boolean;
  error: FetchBaseQueryError | SerializedError | undefined;
};

export const ProductList: React.FC<ProductListProps> = ({ data, isLoading, error }) => {
  const user_id = localStorage.getItem('currentUser')!;

  // Состояние для модалки редактирования:
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [selectedPainting, setSelectedPainting] = useState<Painting | null>(null);

  // Когда нужно открыть редактирование конкретной картины:
  const handleEditClick = (painting: Painting) => {
    setSelectedPainting(painting);
    setIsEditOpen(true);
  };

  // 1) Получаем корзину
  const { data: cartData, isFetching: cartLoading } = useGetCartQuery();

  // 2) Мутации добавления и удаления из корзины и удаления картины
  const [addToCart] = useAddMutation();
  const [removeFromCart] = useDeleteMutation();
  const [deletePainting] = useDeletePaintingMutation();

  // 3) Map<painting.id, cartItem.id> для удаления по реальному ID
  const cartMap = React.useMemo(() => {
    const m = new Map<string, string>();
    cartData?.forEach((item) => {
      m.set(item.painting.id, item.id);
    });
    return m;
  }, [cartData]);

  const handleCartAction = async (paintingId: string, inCart: boolean) => {
    if (inCart) {
      const cartItemId = cartMap.get(paintingId);
      if (cartItemId) {
        await removeFromCart(cartItemId);
      }
    } else {
      await addToCart({ user: user_id, painting_id: paintingId });
    }
  };

  if (isLoading || cartLoading) {
    return (
      <div className={s.root}>
        {[...Array(9)].map((_, i) => (
          <Card key={i} loading />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={s.root}>
        <Text view="p-20">Упс... Какие-то неполадки.</Text>
      </div>
    );
  }

  return (
    <div className={s.root}>
      {data?.results.map((product) => {
        const inCart = cartMap.has(product.id);

        return (
          <Link key={product.id} to={`/main/paintings/${product.id}`} className={s.link}>
            <Card
              image={product.images[0]?.image_url}
              captionSlot={product.category?.name}
              title={product.title}
              subtitle={product.dimensions}
              contentSlot={`${product.price} p`}
              actionSlot={
                <div className={s.button_block}>
                  <Button
                    onClick={(e) => {
                      e.preventDefault();
                      handleCartAction(product.id, inCart);
                    }}
                  >
                    <Text view="button">{inCart ? 'Удалить из корзины' : 'Добавить в корзину'}</Text>
                  </Button>

                  <div className={s.admin_block}>
                    <button
                      className={s.redact}
                      onClick={(e) => {
                        e.preventDefault();
                        handleEditClick(product); // передаём текущий product
                      }}
                    >
                      {/* иконка редактирования */}
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                          d="M13.125 7.125L16.875 10.875M2.625 16.875V21.375H7.125L21.375 7.125L16.875 2.625L2.625 16.875Z"
                          stroke="black"
                          strokeWidth="1.5"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>

                    <button
                      className={s.trash}
                      onClick={(e) => {
                        e.preventDefault();
                        deletePainting(product.id);
                      }}
                    >
                      {/* иконка удаления */}
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path
                          d="M4 7H20M10 11V17M14 11V17M5 7L6 19C6 19.5304 6.21071 20.0391 6.58579 20.4142C6.96086 20.7893 7.46957 21 8 21H16C16.5304 21 17.0391 20.7893 17.4142 20.4142C17.7893 20.0391 18 19.5304 18 19L19 7M9 7V4C9 3.73478 9.10536 3.48043 9.29289 3.29289C9.48043 3.10536 9.73478 3 10 3H14C14.2652 3 14.5196 3.10536 14.7071 3.29289C14.8946 3.48043 15 3.73478 15 4V7"
                          stroke="black"
                          strokeWidth="2"
                          strokeLinecap="round"
                          strokeLinejoin="round"
                        />
                      </svg>
                    </button>
                  </div>
                </div>
              }
            />
          </Link>
        );
      })}

      {/* Модал для редактирования: рендерим вне цикла, но передаем selectedPainting */}
      {selectedPainting && (
        <EditPaintingModal
          isOpen={isEditOpen}
          onClose={() => {
            setIsEditOpen(false);
            setSelectedPainting(null);
          }}
          paintingToEdit={selectedPainting}
        />
      )}
    </div>
  );
};

export default ProductList;
