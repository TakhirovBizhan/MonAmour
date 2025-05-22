
import { createContext, useContext } from 'react';

export type themeTypes = 'light' | 'dark';

interface ThemeContextType {
    theme: themeTypes;
    setTheme: (theme: themeTypes) => void;
}


export const ThemeContext = createContext<ThemeContextType | undefined>(
    undefined
);

export const useTheme = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useTheme must be used within a ThemeProvider');
    }
    return context;
};
