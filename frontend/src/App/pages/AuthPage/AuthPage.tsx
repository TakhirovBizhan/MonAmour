// pages/AuthPage.tsx
import { useForm } from 'react-hook-form';
import s from './AuthPage.module.scss';
import Text from '../../../components/Text';
import { useState } from 'react';
import Button from '../../../components/Button';
import eyeIcon from '../../../../public/eyeIcon.svg';
import eyeIconOff from '../../../../public/eyeIconOff.svg';
import { useRegisterMutation, useLoginMutation } from '../../../store/api/Auth.api';
import { useAuth } from '../../../hooks/useAuth/useAuth';
import { useNavigate } from 'react-router-dom';

// Типы запросов:
type RegisterForm = {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
};
type LoginForm = {
  username: string;
  password: string;
};

type AuthType = 'register' | 'login';

function AuthPage() {
  const {
    register: registerField,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm & LoginForm>();

  const [authMode, setAuthMode] = useState<AuthType>('register');
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  const [registerUser, { isLoading: isRegisterLoading, error: registerError }] = useRegisterMutation();
  const [loginUser, { isLoading: isLoginLoading, error: loginError }] = useLoginMutation();

  const onSubmit = async (data: RegisterForm & LoginForm) => {
    try {
      if (authMode === 'register') {
        const regData: RegisterForm = {
          username: (data as RegisterForm).username,
          email: (data as RegisterForm).email,
          password: (data as RegisterForm).password,
          password2: (data as RegisterForm).password2,
          first_name: (data as RegisterForm).first_name,
          last_name: (data as RegisterForm).last_name,
          phone: (data as RegisterForm).phone,
        };
        const response = await registerUser(regData).unwrap();
        // После регистрации логинимся: API MyTokenObtainPairSerializer возвращает {access, refresh, user}
        const loginRes = await loginUser({ username: response.username, password: regData.password }).unwrap();
        authLogin(loginRes.access, loginRes.refresh, loginRes.user);
        navigate('/'); // или нужный маршрут
      } else {
        const loginData: LoginForm = {
          username: (data as LoginForm).username,
          password: (data as LoginForm).password,
        };
        const response = await loginUser(loginData).unwrap();
        authLogin(response.access, response.refresh, response.user);
        navigate('/');
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      // Можно дополнительно обрабатывать и показывать ошибки
    }
  };

  const toggleAuth = () => {
    setAuthMode((prev) => (prev === 'register' ? 'login' : 'register'));
  };

  return (
    <fieldset className={s.fieldset}>
      <legend>
        <Text view="title" color="primary">
          {authMode === 'register' ? 'Registration' : 'Login'}
        </Text>
      </legend>
      <form noValidate className={s.form} onSubmit={handleSubmit(onSubmit)}>
        {authMode === 'register' && (
          <>
            <label htmlFor="username">
              Username*
              <input id="username" required {...registerField('username', { required: 'Username required' })} />
              {errors.username && <p>{errors.username.message}</p>}
            </label>
            <label htmlFor="email">
              Email*
              <input id="email" required type="email" {...registerField('email', { required: 'Email required' })} />
              {errors.email && <p>{errors.email.message}</p>}
            </label>
            <label htmlFor="password">
              Password*
              <div className={s.password_wrapper}>
                <input
                  id="password"
                  required
                  minLength={6}
                  type={showPassword ? 'text' : 'password'}
                  {...registerField('password', {
                    required: 'Password required',
                    minLength: { value: 6, message: '6 symbols minimum' },
                  })}
                />
                <img
                  className={s.eye_icon}
                  onClick={() => setShowPassword((prev) => !prev)}
                  src={showPassword ? eyeIconOff : eyeIcon}
                  alt="Toggle password visibility"
                />
              </div>
              {errors.password && <p>{errors.password.message}</p>}
            </label>
            <label htmlFor="password2">
              Confirm Password*
              <input
                id="password2"
                required
                minLength={6}
                type={showPassword ? 'text' : 'password'}
                {...registerField('password2', {
                  required: 'Confirm password required',
                  minLength: { value: 6, message: '6 symbols minimum' },
                })}
              />
              {errors.password2 && <p>{errors.password2.message}</p>}
            </label>
            <label htmlFor="first_name">
              First Name
              <input id="first_name" {...registerField('first_name')} />
            </label>
            <label htmlFor="last_name">
              Last Name
              <input id="last_name" {...registerField('last_name')} />
            </label>
            <label htmlFor="phone">
              Phone
              <input id="phone" {...registerField('phone')} />
            </label>
          </>
        )}
        {authMode === 'login' && (
          <>
            <label htmlFor="username">
              Username*
              <input id="username" required {...registerField('username', { required: 'Username required' })} />
              {errors.username && <p>{errors.username.message}</p>}
            </label>
            <label htmlFor="password">
              Password*
              <div className={s.password_wrapper}>
                <input
                  id="password"
                  required
                  minLength={6}
                  type={showPassword ? 'text' : 'password'}
                  {...registerField('password', {
                    required: 'Password required',
                    minLength: { value: 6, message: '6 symbols minimum' },
                  })}
                />
                <img
                  className={s.eye_icon}
                  onClick={() => setShowPassword((prev) => !prev)}
                  src={showPassword ? eyeIconOff : eyeIcon}
                  alt="Toggle password visibility"
                />
              </div>
              {errors.password && <p>{errors.password.message}</p>}
            </label>
          </>
        )}
        <Button className={s.submit_btn} type="submit" disabled={isRegisterLoading || isLoginLoading}>
          {authMode === 'register' ? 'Register' : 'Login'}
        </Button>

        {authMode === 'register' && registerError && (
          <p className={s.error_message}>Registration Error: {JSON.stringify(registerError)}</p>
        )}
        {authMode === 'login' && loginError && (
          <p className={s.error_message}>Login Error: {JSON.stringify(loginError)}</p>
        )}
      </form>

      <button onClick={toggleAuth} className={s.assign_link}>
        {authMode === 'register' ? 'Have an account? Login here' : "Don't have an account? Register"}
      </button>
    </fieldset>
  );
}

export default AuthPage;
