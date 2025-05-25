import { api } from "./api";

type cartPostType = {
    user_id: string,
    painting_id: string
}

export const CartApi = api.injectEndpoints({
    endpoints: builder => ({

        add: builder.mutation<void, cartPostType>({
            query: (regData) => ({
                url: "/carts",
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
    })
})

export const { useAddMutation, useDeleteMutation } = CartApi;