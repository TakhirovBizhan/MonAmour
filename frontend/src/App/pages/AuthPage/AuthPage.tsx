import { useForm } from 'react-hook-form';
import s from './AuthPage.module.scss';
import Text from '../../../components/Text';
import { useState } from 'react';
import Button from '../../../components/Button';
import eyeIcon from '../../../../public/eyeIcon.svg';
import eyeIconOff from '../../../../public/eyeIconOff.svg';
import { userLogType, userRegType } from '../../../config/DataInterfaces';
import { useRegisterMutation, useLoginMutation } from '../../../store/api/Auth.api';
import { useAuth } from '../../../hooks/useAuth/AuthContext';
import { useNavigate } from 'react-router-dom';

type AuthType = 'register' | 'login';

type FormData = userRegType | userLogType;

function AuthPage() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>();

  const { login } = useAuth();
  const navigate = useNavigate();
  const [authIs, setAuthIs] = useState<AuthType>('register');
  const [showPassword, setShowPassword] = useState(false);

  const [registerUser, { isLoading: isRegisterLoading, error: registerError }] = useRegisterMutation();
  const [loginUser, { isLoading: isLoginLoading, error: loginError }] = useLoginMutation();

  const onSubmit = async (data: FormData) => {
    try {
      if (authIs === 'register') {
        const regData = data as userRegType;
        const response = await registerUser({
          ...regData,
          avatar: 'https://docs.gravatar.com/wp-content/uploads/2025/02/avatar-mysteryperson-20250210-256.png?w=256',
        }).unwrap();
        const logResponce = await loginUser({ email: response.email, password: response.password }).unwrap();
        login(logResponce.access_token);
        navigate('/main');
      } else {
        const loginData = data as userLogType;
        const response = await loginUser(loginData).unwrap();
        login(response.access_token);
        navigate('/main');
      }
    } catch (err) {
      console.error('API error:', err);
    }
  };

  const toggleAuth = () => {
    setAuthIs((prev) => (prev === 'register' ? 'login' : 'register'));
  };

  return (
    <fieldset className={s.fieldset}>
      <legend>
        <Text view="title" color="primary">
          {authIs === 'register' ? 'Registration' : 'Login'}
        </Text>
      </legend>
      <form noValidate className={s.form} onSubmit={handleSubmit(onSubmit)}>
        {authIs === 'register' && (
          <label htmlFor="name">
            Full name
            <input id="name" required {...register('name', { required: 'Name required' })} />
          </label>
        )}

        <label htmlFor="email">
          Email
          <input id="email" required type="email" {...register('email', { required: 'Email required' })} />
        </label>
        {errors.email && <p>{errors.email.message}</p>}

        <label className={s.password_label} htmlFor="password">
          Password
          <input
            id="password"
            required
            minLength={6}
            className={s.password_input}
            type={showPassword ? 'text' : 'password'}
            {...register('password', {
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
        </label>
        {errors.password && <p>{errors.password.message}</p>}

        <Button className={s.submit_btn} type="submit" disabled={isRegisterLoading || isLoginLoading}>
          {authIs === 'register' ? 'Register' : 'Login'}
        </Button>

        {authIs === 'register' && registerError && (
          <p className={s.error_message}>Registration Error: {JSON.stringify(registerError)}</p>
        )}
        {authIs === 'login' && loginError && (
          <p className={s.error_message}>Login Error: {JSON.stringify(loginError)}</p>
        )}
      </form>

      <button onClick={toggleAuth} className={s.assign_link}>
        {authIs === 'register' ? 'Have an account? Login here' : "Don't have an account? Register"}
      </button>
    </fieldset>
  );
}

export default AuthPage;
