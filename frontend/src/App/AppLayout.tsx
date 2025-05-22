import { Outlet, Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth/AuthContext';
import Header from '../components/Header';

const ProtectedLayout = () => {
  const { isAuthenticated } = useAuth();

  return (
    <>
      <Header />
      {isAuthenticated ? <Outlet /> : <Navigate to="/login" />}
    </>
  );
};

export default ProtectedLayout;
