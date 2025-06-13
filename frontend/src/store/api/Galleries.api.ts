import { api } from "./api";

export type galleryResponce = {
    "id": string,
    "name": string,
    "description": string,
    "gallery_image": string
};

export const CartApi = api.injectEndpoints({
    endpoints: (builder) => ({

        getGalleries: builder.query<galleryResponce[], void>({
            query: () => ({
                url: `/galleries/`,
                method: "GET",
            }),
        }),
    }),
});

export const {
    useGetGalleriesQuery,
} = CartApi;