import { api } from "./api";

export type artistResponce = {
    "id": string,
    "name": string,
    "image": string,
    "biography": string,
    "resume": null,
    "website": null,
    "average_rating": 4.0 | null,
    "reviews_count": number
};

export const CartApi = api.injectEndpoints({
    endpoints: (builder) => ({

        getArtists: builder.query<artistResponce[], void>({
            query: () => ({
                url: `/artists/`,
                method: "GET",
            }),
        }),

        getArtist: builder.query<artistResponce, string>({
            query: (id) => ({
                url: `/artists/${id}`,
                method: "GET",
            }),
        }),
    }),
});

export const {
    useGetArtistsQuery,
    useGetArtistQuery
} = CartApi;