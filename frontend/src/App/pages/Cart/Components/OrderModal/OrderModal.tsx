import React, { useState } from 'react';
import s from './OrderModal.module.scss';
import Text from '../../../../../components/Text';
import Button from '../../../../../components/Button';
import { Painting } from '../../../../../config/DataInterfaces';
import { useNavigate } from 'react-router-dom';
import { usePostOrderMutation } from '../../../../../store/api/Orders.api';

export interface CartItem {
  cartItemId: string;
  painting: Painting;
}

interface OrderModalProps {
  isOpen: boolean;
  onClose: () => void;
  cartItems: CartItem[];
  removeFromCart: (id: string) => any;
}

const OrderModal: React.FC<OrderModalProps> = ({ isOpen, onClose, cartItems, removeFromCart }) => {
  const navigate = useNavigate();
  const [street, setStreet] = useState('');
  const [houseNumber, setHouseNumber] = useState('');
  const [city, setCity] = useState('');
  const [postalCode, setPostalCode] = useState('');
  const [addressComment, setAddressComment] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'cash'>('card');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState<string | null>(null);

  const [postOrder, { isLoading: isPosting }] = usePostOrderMutation();
  const userId = localStorage.getItem('currentUser') || '';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!street.trim() || !houseNumber.trim() || !city.trim() || !postalCode.trim()) {
      setError('Пожалуйста, заполните все обязательные поля адреса.');
      return;
    }
    if (!phoneNumber.trim()) {
      setError('Пожалуйста, укажите контактный номер телефона.');
      return;
    }
    // Простейшая проверка телефона: минимум 7 цифр
    if (!/^\+?\d{7,15}$/.test(phoneNumber.trim())) {
      setError('Неверный формат телефона. Например: +79261234567');
      return;
    }
    if (cartItems.length === 0) {
      setError('В корзине нет картин для заказа.');
      return;
    }

    const payload = {
      user_id: userId,
      status: 'processing',
      street: street.trim(),
      house_number: houseNumber.trim(),
      city: city.trim(),
      postal_code: postalCode.trim(),
      address_comment: addressComment.trim() || undefined,
      payment_method: paymentMethod,
      phone_number: phoneNumber.trim(),
      painting_ids: cartItems.map((ci) => ci.painting.id),
    };

    try {
      const createdOrder = await postOrder(payload).unwrap();
      for (const ci of cartItems) {
        try {
          await removeFromCart(ci.cartItemId).unwrap();
        } catch (errRemove) {
          console.error('Ошибка удаления из корзины после заказа', errRemove);
        }
      }
      onClose();
      navigate(`/order/${createdOrder.id}`, { state: { order: createdOrder } });
    } catch (err: any) {
      console.error('Ошибка при создании заказа:', err);
      if (err?.data) {
        const msg = (err.data as any).detail || JSON.stringify(err.data as any) || 'Ошибка при оформлении заказа';
        setError(msg);
      } else {
        setError(err.message || 'Ошибка при оформлении заказа');
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className={s.overlay} onClick={onClose}>
      <div className={s.modal} onClick={(e) => e.stopPropagation()}>
        <Button className={s.closeBtn} onClick={onClose}>
          &times;
        </Button>
        <Text view="title">Оформление заказа</Text>
        <div className={s.itemsList}>
          <Text view="p-18">Выбранные картины:</Text>
          <ul>
            {cartItems.map((ci) => (
              <li key={ci.cartItemId} className={s.itemRow}>
                <Text view="p-18">
                  {ci.painting.title} — {ci.painting.price} р
                </Text>
              </li>
            ))}
          </ul>
        </div>
        <form className={s.form} onSubmit={handleSubmit} noValidate>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Улица*</Text>
              <input type="text" value={street} onChange={(e) => setStreet(e.target.value)} required />
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Номер дома*</Text>
              <input type="text" value={houseNumber} onChange={(e) => setHouseNumber(e.target.value)} required />
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Город*</Text>
              <input type="text" value={city} onChange={(e) => setCity(e.target.value)} required />
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Почтовый индекс*</Text>
              <input type="text" value={postalCode} onChange={(e) => setPostalCode(e.target.value)} required />
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Комментарий к адресу</Text>
              <textarea value={addressComment} onChange={(e) => setAddressComment(e.target.value)} rows={3} />
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Способ оплаты*</Text>
              <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value as 'card' | 'cash')}>
                <option value="card">Картой</option>
                <option value="cash">Наличными</option>
              </select>
            </label>
          </div>
          <div className={s.formGroup}>
            <label>
              <Text view="p-18">Телефон*</Text>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                placeholder="Например: +79261234567"
              />
            </label>
          </div>
          {error && (
            <div className={s.errorMsg}>
              <Text view="p-18">{error}</Text>
            </div>
          )}
          <div className={s.actions}>
            <Button type="submit" disabled={isPosting}>
              {isPosting ? 'Оформляем...' : 'Подтвердить заказ'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default OrderModal;
