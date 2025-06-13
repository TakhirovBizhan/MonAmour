// store/api/Products.api.ts
import { IPaintingData, PaintingPostType, TFilters } from "../../config/DataInterfaces";
import { api } from "./api";

// Описание типа, который возвращает uploadImageBase64. 
// Подкорректируйте в соответствии с тем, что реально возвращает ваш бэкенд.
interface UploadedImageResponse {
    id: string;
    image_url: string;
}

export const productsApi = api.injectEndpoints({
    endpoints: builder => ({
        getProducts: builder.query<IPaintingData, { page?: number; rangeFilter?: TFilters; search?: string; category?: string; gallery?: string; sort?: string } | void>({
            query: ({ page = 0, rangeFilter = { price_min: null, price_max: null }, search = '', category, gallery, sort } = {}) => {
                const urlParams = new URLSearchParams();
                urlParams.append("offset", ((page - 1) * 9).toString());
                urlParams.append("limit", '9');

                if (category) {
                    urlParams.set('category', category);
                } else {
                    urlParams.delete('category');
                }
                if (sort) {
                    urlParams.set('sort', sort);
                } else {
                    urlParams.delete('sort');
                }

                if (gallery) {
                    urlParams.set('gallery', gallery);
                } else {
                    urlParams.delete('gallery');
                }
                if (rangeFilter.price_min != null && rangeFilter.price_max != null) {
                    urlParams.set('max_price', rangeFilter.price_max.toString());
                    urlParams.set('min_price', rangeFilter.price_min.toString());
                } else {
                    urlParams.delete('min_price');
                    urlParams.delete('max_price');
                }

                if (search) {
                    urlParams.set('title', search);
                } else {
                    urlParams.delete('title');
                }

                return `/paintings?${urlParams.toString()}`;
            },
        }),

        addPainting: builder.mutation<void, PaintingPostType>({
            query: (regData) => ({
                url: "/paintings/",
                method: "POST",
                body: regData,
            }),
        }),

        // Новый endpoint для загрузки одного изображения в base64-формате:
        uploadImageBase64: builder.mutation<UploadedImageResponse, { image: string }>({
            query: ({ image }) => ({
                url: "/painting-images/",   // или "/api/painting-images/" в зависимости от маршрутов
                method: "POST",
                body: { image },            // сериализатор PaintingImageUploadSerializer ожидает поле "image"
            }),
        }),
    }),
    overrideExisting: false,
});

export const { useGetProductsQuery, useAddPaintingMutation, useUploadImageBase64Mutation } = productsApi;