import { Painting } from "../../config/DataInterfaces";
import { api } from "./api";

type cartPostType = {
    user: string,
    painting_id: string
}

type cartResponce = {
    id: string,
    user: string,
    painting: Painting
}

export const CartApi = api.injectEndpoints({
    endpoints: builder => ({

        add: builder.mutation<void, cartPostType>({
            query: (regData) => ({
                url: "/carts/",
                method: "POST",
                body: regData,
            }),
        }),
        delete: builder.mutation<void, string>({
            query: (logData) => ({
                url: `/carts/${logData}`,
                method: "DELETE"
            }),
        }),

        getCart: builder.query<cartResponce[], void>({
            query: () => ({
                url: `/carts/?user=${localStorage.getItem('currentUser')}`,
                method: "GET"
            }),
        })
    })
})

export const { useAddMutation, useDeleteMutation, useGetCartQuery } = CartApi;