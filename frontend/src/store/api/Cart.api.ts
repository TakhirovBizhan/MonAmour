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

        add: builder.mutation<void, cartPostType>({
            query: (regData) => ({
                url: "/carts/",
                method: "POST",
                body: regData,
            }),
            invalidatesTags: [{ type: 'Cart', id: 'LIST' }],  // ← после добавления перезапросить список
        }),

        delete: builder.mutation<void, string>({
            query: (cartId) => ({
                url: `/carts/${cartId}`,
                method: "DELETE",
            }),
            invalidatesTags: [{ type: 'Cart', id: 'LIST' }],  // ← после удаления перезапросить список
        }),

        getCart: builder.query<cartResponce[], void>({
            query: () => ({
                url: `/carts/?user=${localStorage.getItem('currentUser')}`,
                method: "GET",
            }),
            providesTags: (result) =>
                result
                    ? [
                        // тэг на весь список
                        { type: 'Cart' as const, id: 'LIST' },
                        // плюс тэги на отдельные элементы, если нужно
                        ...result.map(({ id }) => ({ type: 'Cart' as const, id })),
                    ]
                    : [{ type: 'Cart' as const, id: 'LIST' }],
        }),

    }),
    overrideExisting: false,
});

export const {
    useAddMutation,
    useDeleteMutation,
    useGetCartQuery,
} = CartApi;