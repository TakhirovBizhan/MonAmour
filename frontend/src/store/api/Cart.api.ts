import { Painting } from "../../config/DataInterfaces";
import { api } from "./api";

type cartPostType = {
    user: string;
    painting_id: string;
};

export type cartResponce = {
    id: string;
    user: string;
    painting: Painting;
};

export const CartApi = api.injectEndpoints({
    endpoints: (builder) => ({

        add: builder.mutation<void, { painting_id: string }>({
            query: ({ painting_id }) => ({
                url: '/carts/',
                method: 'POST',
                body: { painting_id },
            }),
            invalidatesTags: [{ type: 'Cart', id: 'LIST' }],
        }),
        getCart: builder.query<any[], void>({
            query: () => ({ url: '/carts/' }),
            providesTags: (result) => result
                ? [
                    { type: 'Cart' as const, id: 'LIST' },
                    ...result.map(item => ({ type: 'Cart' as const, id: item.id })),
                ]
                : [{ type: 'Cart' as const, id: 'LIST' }],
        }),
        delete: builder.mutation<void, string>({
            query: (cartId) => ({
                url: `/carts/${cartId}/`,
                method: 'DELETE',
            }),
            invalidatesTags: [{ type: 'Cart', id: 'LIST' }],
        }),

    }),
    overrideExisting: false,
});

export const {
    useAddMutation,
    useDeleteMutation,
    useGetCartQuery,
} = CartApi;