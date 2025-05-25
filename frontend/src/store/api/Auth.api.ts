import { userRegType, userRegResponce, userLogType, userLogResponce } from "../../config/DataInterfaces";
import { api } from "./api";


type updateUserType = {
    id: string,
    username: string,
    email: string,
    first_name: string,
    last_name: string
}
// пока не пользуемся авторизацией


export const AuthApi = api.injectEndpoints({
    endpoints: builder => ({

        register: builder.mutation<userRegResponce, userRegType>({
            query: (regData) => ({
                url: "/users",
                method: "POST",
                body: regData,
            }),
        }),
        login: builder.mutation<userLogResponce, userLogType>({
            query: (logData) => ({
                url: "/auth/login",
                method: "POST",
                body: logData,
            }),
        }),
        getProfile: builder.query<userRegResponce, string>({
            query: (logData) => ({
                url: `/users/${logData}/`,
                method: "GET"

                /* headers: {
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
                }, */
            }),
        }),

        update: builder.mutation<void, updateUserType>({
            query: (logData) => ({
                url: `/users/${logData.id}/`,
                method: "PUT",
                body: logData,
            }),
        }),

    })
})

export const { useRegisterMutation, useLoginMutation, useUpdateMutation, useGetProfileQuery } = AuthApi;