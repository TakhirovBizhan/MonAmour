import React, { useState, useEffect } from 'react';
import { ThemeContext, themeTypes } from './themeContext';

type ThemeProps = {
  children: React.ReactNode;
};

export const ThemeProvider: React.FC<ThemeProps> = ({ children }) => {
  const [theme, setTheme] = useState<themeTypes>(() => {
    const storedTheme = localStorage.getItem('theme');
    return storedTheme === 'light' || storedTheme === 'dark' ? (storedTheme as themeTypes) : 'light';
  });

  useEffect(() => {
    document.body.classList.remove('light', 'dark');
    document.body.classList.add(theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
};
