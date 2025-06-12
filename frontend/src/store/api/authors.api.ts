import { api } from "./api";

export type artistResponce = {
    "id": string,
    "name": string,
    "image": string,
    "biography": string,
    "resume": null,
    "website": null
};

export const CartApi = api.injectEndpoints({
    endpoints: (builder) => ({

        getArtists: builder.query<artistResponce[], void>({
            query: () => ({
                url: `/artists/`,
                method: "GET",
            }),
        }),
    }),
});

export const {
    useGetArtistsQuery,
} = CartApi;