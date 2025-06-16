import React, { useState } from 'react';
import Loader from '../../../components/Loader';
import Text from '../../../components/Text';
import s from './Profile.module.scss';
import Redact from './components/redact';
import Button from '../../../components/Button';
import { useGetMeQuery } from '../../../store/api/Auth.api';
import { useAuth } from '../../../hooks/useAuth/useAuth';
import { useNavigate, Link } from 'react-router-dom';
import { useGetOrdersQuery } from '../../../store/api/Orders.api'; // импорт

const Profile = () => {
  const { data: profileData, isLoading: loadingProfile, isError: errorProfile } = useGetMeQuery();
  const [isModalOpen, setModalOpen] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  // Получаем список заказов
  const { data: orders, isLoading: loadingOrders, isError: errorOrders } = useGetOrdersQuery();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  if (loadingProfile) {
    return (
      <div className={s.wrapper}>
        <Loader size="l" />
      </div>
    );
  }
  if (errorProfile || !profileData) {
    return (
      <div className={s.wrapper}>
        <Text view="title">Ошибка загрузки профиля</Text>
      </div>
    );
  }

  return (
    <div className={s.wrapper}>
      {/* Профиль */}
      <div className={s.root}>
        <img
          className={s.img}
          src={`https://avatar.iran.liara.run/username?username=${profileData.first_name || profileData.username}`}
          alt={'avatar'}
        />
        <div>
          <div className={s.title_block}>
            <Text view="min-title">Имя пользователя: {profileData.username}</Text>
            <button className={s.redact} onClick={() => setModalOpen(true)}>
              {/* Иконка редактирования */}
              <svg width="25" height="25" viewBox="0 0 35 35" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path
                  d="M32.0832 10.5587C32.0843 10.3668 32.0475 10.1765 31.9749 9.99882C31.9024 9.82114 31.7954 9.65953 31.6603 9.52327L25.4769 3.33993C25.3407 3.20477 25.1791 3.09784 25.0014 3.02527C24.8237 2.95269 24.6335 2.91591 24.4415 2.91702C24.2496 2.91591 24.0593 2.95269 23.8817 3.02527C23.704 3.09784 23.5424 3.20477 23.4061 3.33993L19.279 7.46702L3.33944 23.4066C3.20428 23.5429 3.09735 23.7045 3.02478 23.8822C2.95221 24.0598 2.91542 24.2501 2.91653 24.442V30.6254C2.91653 31.0121 3.07017 31.3831 3.34366 31.6565C3.61715 31.93 3.98809 32.0837 4.37486 32.0837H10.5582C10.7623 32.0948 10.9664 32.0629 11.1573 31.99C11.3482 31.9172 11.5217 31.805 11.6665 31.6608L27.5186 15.7212L31.6603 11.667C31.7932 11.5255 31.9016 11.3629 31.9811 11.1858C31.9952 11.0695 31.9952 10.952 31.9811 10.8358C31.9879 10.7679 31.9879 10.6995 31.9811 10.6316L32.0832 10.5587ZM9.96028 29.167H5.83319V25.0399L20.3144 10.5587L24.4415 14.6858L9.96028 29.167ZM26.4978 12.6295L22.3707 8.50243L24.4415 6.44618L28.554 10.5587L26.4978 12.6295Z"
                  fill="black"
                />
              </svg>
            </button>
          </div>
          <Redact data={profileData!} isOpen={isModalOpen} onClose={() => setModalOpen(false)} />
          <Text view="p-18">Почта: {profileData.email}</Text>
          <Text view="p-18">Имя: {profileData.first_name}</Text>
          <Text view="p-18">Фамилия: {profileData.last_name}</Text>
          {profileData.phone && <Text view="p-18">Телефон: {profileData.phone}</Text>}
        </div>
      </div>

      <Button className={s.button} onClick={handleLogout}>
        Выход
      </Button>

      {/* Блок «Мои заказы» */}
      <div className={s.ordersSection}>
        <Text view="min-title">Мои заказы</Text>

        {loadingOrders ? (
          <Loader size="l" />
        ) : errorOrders ? (
          <Text view="p-18">Ошибка загрузки заказов.</Text>
        ) : orders && orders.length > 0 ? (
          <div className={s.orderList}>
            {orders.map((order) => (
              <Link to={`/order/${order.id}`} key={order.id} className={s.orderCard}>
                <div className={s.orderInfo}>
                  <Text view="p-16">Заказ #{order.id}</Text>
                  <Text view="p-14" color="secondary">
                    Дата: {new Date(order.order_date).toLocaleString?.() ?? new Date(order.order_date).toLocaleString()}
                  </Text>
                  <Text view="p-14" color="secondary">
                    Статус: {order.status}
                  </Text>
                </div>
                {/* Покажем превью первой картины, если есть */}
                {order.items && order.items.length > 0 && (
                  <div className={s.orderItemsPreview}>
                    {order.items.slice(0, 3).map((item) => (
                      <div key={item.id} className={s.orderItemPreview}>
                        <img
                          src={item.painting.images?.[0]?.image_url}
                          alt={item.painting.title}
                          className={s.orderItemImage}
                        />
                        <Text view="p-14" className={s.orderItemTitle}>
                          {item.painting.title}
                        </Text>
                      </div>
                    ))}
                    {order.items.length > 3 && (
                      <Text view="p-14" className={s.moreItems}>
                        +{order.items.length - 3} ещё
                      </Text>
                    )}
                  </div>
                )}
              </Link>
            ))}
          </div>
        ) : (
          <Text view="p-18">У вас пока нет заказов.</Text>
        )}
      </div>
    </div>
  );
};

export default Profile;
