import { useContext } from 'react';
import { ThemeContext } from '../../hooks/useThemes/themeContext';
import moon from '../../../public/moon.svg';
import sun from '../../../public/sun.svg';
import s from './ThemeButton.module.scss';

export const ThemeToggle = () => {
  const themeContext = useContext(ThemeContext);

  if (!themeContext) {
    return null;
  }

  const { theme, setTheme } = themeContext;

  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  return (
    <button onClick={toggleTheme} className={s.button}>
      <img className={s.img} src={theme === 'dark' ? moon : sun} />
    </button>
  );
};
