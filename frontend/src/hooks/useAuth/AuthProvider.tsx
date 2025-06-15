// hooks/useAuth/AuthProvider.tsx
import React, { useEffect, useState } from 'react';
import { AuthContext } from './AuthContext';
import { useGetMeQuery, useRefreshTokenMutation } from '../../store/api/Auth.api';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const storedAccess = localStorage.getItem('accessToken');
  const storedRefresh = localStorage.getItem('refreshToken');

  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!storedAccess);
  const [user, setUser] = useState<any | null>(null);
  const [initialized, setInitialized] = useState<boolean>(false);

  // RTK Query hook, skip если токена нет
  const {
    data: meData,
    isLoading: meLoading,
    isSuccess: meSuccess,
    isError: meError,
    refetch: refetchMe,
  } = useGetMeQuery(undefined, { skip: !storedAccess });

  // Можно настроить refresh logic, но пока просто рефетчим профиль
  useEffect(() => {
    if (storedAccess) {
      refetchMe();
    } else {
      // сразу отмечаем, что инициализация завершена, пользователь не аутентифицирован
      setInitialized(true);
      setIsAuthenticated(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storedAccess]);

  // Когда ответ от getMe приходит:
  useEffect(() => {
    if (meSuccess && meData) {
      setUser(meData);
      setIsAuthenticated(true);
      setInitialized(true);
    } else if (meError) {
      // токен недействителен или не удалось получить профиль
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setIsAuthenticated(false);
      setInitialized(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [meSuccess, meError, meData]);

  const login = async (accessToken: string, refreshToken: string, userData?: any) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
    setIsAuthenticated(true);
    if (userData) {
      setUser(userData);
    } else {
      // запросим профиль
      try {
        await refetchMe();
      } catch {}
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setIsAuthenticated(false);
    setUser(null);
  };

  // Пока не закончили инициализацию (initialized=false), можно рендерить Loader или null
  if (!initialized) {
    return <div>Загрузка...</div>;
  }

  return <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>{children}</AuthContext.Provider>;
};
