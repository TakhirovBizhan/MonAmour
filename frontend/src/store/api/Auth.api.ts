import { userRegType, userRegResponce, userLogType, userLogResponce } from "../../config/DataInterfaces";
import { api } from "./api";

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
        getProfile: builder.query<userRegResponce, void>({
            query: (logData) => ({
                url: "/auth/profile",
                method: "GET",
                body: logData,
                headers: {
                    Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
                },
            }),
        }),
    })
})

export const { useRegisterMutation, useLoginMutation, useGetProfileQuery } = AuthApi;