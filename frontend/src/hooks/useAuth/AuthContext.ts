// hooks/useAuth/AuthContext.tsx
import React from "react";

export interface AuthContextType {
    isAuthenticated: boolean;
    user: any | null;
    login: (accessToken: string, refreshToken: string, userData: any) => void;
    logout: () => void;
}

export const AuthContext = React.createContext<AuthContextType>({
    isAuthenticated: false,
    user: null,
    login: () => { },
    logout: () => { },
});