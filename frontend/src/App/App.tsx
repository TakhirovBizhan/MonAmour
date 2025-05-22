import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AboutUs, Cart, Categories, MainPage, ProductPage, AuthPage, Profile } from './pages';
import { ROUTES } from '../config/routes';
import { ThemeProvider } from '../hooks/useThemes/themeProvider';
import ProtectedLayout from './AppLayout';
import { AuthProvider } from '../hooks/useAuth/AuthProvider';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<AuthPage />} />

            <Route path="/" element={<ProtectedLayout />}>
              <Route path={ROUTES.root} element={<MainPage />} />
              <Route path={ROUTES.category} element={<MainPage />} />
              <Route path={ROUTES.product} element={<ProductPage />} />
              <Route path={ROUTES.categories} element={<Categories />} />
              <Route path={ROUTES.about_us} element={<AboutUs />} />
              <Route path={ROUTES.auth} element={<AuthPage />} />
              <Route path={ROUTES.profile} element={<Profile />} />
              <Route path={ROUTES.cart} element={<Cart />} />
              <Route path="*" element={<Navigate to={ROUTES.root} replace />} />
              <Route path="/" element={<Navigate to={ROUTES.root} replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default App;
