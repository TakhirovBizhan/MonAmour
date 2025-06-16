import { api } from "./api";

export type artistReviewResponce = {
    "id": string,
    "artist": artistResponce,
    "user": string,
    "rating": number,
    "comment": string,
    "created_at": string,
    "updated_at": string
}


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

export type ArtistReviewResponse = {
    id: string;
    artist: artistResponce;
    user: string; // username или id? Ваш сериализатор StringRelatedField даёт str(self.user)
    rating: number;
    comment: string | null;
    created_at: string;
    updated_at: string;
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

        createArtistReview: builder.mutation<ArtistReviewResponse, { artist_id: string; rating: number; comment?: string }>({
            query: ({ artist_id, rating, comment }) => ({
                url: `/artist-reviews/`,
                method: "POST",
                body: { artist_id, rating, comment },
            }),
        }),

        getReviewsByArtist: builder.query<artistReviewResponce[], string>({
            query: (id) => ({
                url: `/artist-reviews/?artist=${id}`,
                method: "GET",
            }),
        }),
    }),
});

export const {
    useGetArtistsQuery,
    useGetArtistQuery,
    useGetReviewsByArtistQuery,
    useCreateArtistReviewMutation
} = CartApi;