// store/api/Auth.api.ts
import {
    userRegType,
    userRegResponce,
    userLogType,
    userLogResponce,
} from '../../config/DataInterfaces';
import { api } from './api';

type updateUserType = {
    id: string;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
};

export const AuthApi = api.injectEndpoints({
    endpoints: (builder) => ({
        register: builder.mutation<userRegResponce, userRegType>({
            query: (regData) => ({
                url: '/users',
                method: 'POST',
                body: regData,
            }),
        }),

        login: builder.mutation<userLogResponce, userLogType>({
            query: (logData) => ({
                url: '/auth/login',
                method: 'POST',
                body: logData,
            }),
        }),

        getProfile: builder.query<userRegResponce, string>({
            query: (userId) => ({
                url: `/users/${userId}/`,
                method: 'GET',
            }),
            providesTags: (result, error, userId) => [
                { type: 'User', id: userId },
            ],
        }),

        updateUser: builder.mutation<userRegResponce, updateUserType>({
            query: (data) => ({
                url: `/users/${data.id}/`,
                method: 'PUT',
                body: data,
            }),
            invalidatesTags: (result, error, { id }) => [
                { type: 'User', id },
            ],
        }),
    }),
    overrideExisting: false,
});

export const {
    useRegisterMutation,
    useLoginMutation,
    useGetProfileQuery,
    useUpdateUserMutation,  // ← обратите внимание, что хук называется по-новому
} = AuthApi;