// store/api/Auth.api.ts
import { api } from "./api";
import { User } from "../../config/DataInterfaces";

type updateUserType = {
    id: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
};


interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    password2: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
    // role не передаем при обычной регистрации, сервер сам поставит 'buyer'
}
interface RegisterResponse {
    id: string;
    username: string;
    email: string;
    first_name?: string;
    last_name?: string;
    phone?: string;
    role?: string;
    date_joined: string;
}
interface TokenResponse {
    access: string;
    refresh: string;
    user: User; // потому что MyTokenObtainPairSerializer возвращает user
}
interface LoginRequest {
    username: string;
    password: string;
}

export const AuthApi = api.injectEndpoints({
    endpoints: (builder) => ({

        updateUser: builder.mutation<RegisterResponse, updateUserType>({
            query: (data) => ({
                url: `/users/${data.id}/`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (result, error, { id }) => [
                { type: 'User', id },
            ],
        }),

        register: builder.mutation<RegisterResponse, RegisterRequest>({
            query: (regData) => ({
                url: "/auth/register/",
                method: "POST",
                body: regData,
            }),
        }),
        login: builder.mutation<TokenResponse, LoginRequest>({
            query: (logData) => ({
                url: "/auth/token/",
                method: "POST",
                body: logData,
            }),
        }),
        refreshToken: builder.mutation<{ access: string; refresh: string }, { refresh: string }>({
            query: ({ refresh }) => ({
                url: "/auth/token/refresh/",
                method: "POST",
                body: { refresh },
            }),
        }),
        getMe: builder.query<User, void>({
            query: () => ({
                url: "/auth/me/",
                method: "GET",
            }),
            providesTags: (result) =>
                result ? [{ type: "User" as const, id: result.id }] : [{ type: "User" as const, id: "LIST" }],
        }),
    }),
    overrideExisting: false,
});

export const {
    useRegisterMutation,
    useLoginMutation,
    useRefreshTokenMutation,
    useGetMeQuery,
    useUpdateUserMutation
} = AuthApi;
