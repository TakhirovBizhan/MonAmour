import { IData, TFilters } from "../../config/DataInterfaces";
import { api } from "./api";


export const productsApi = api.injectEndpoints({
    endpoints: builder => ({
        getProducts: builder.query<IData[], { page?: number, rangeFilter?: TFilters, search?: string, category?: number } | void>({
            query: ({ page = 0, rangeFilter = { price_min: null, price_max: null }, search = '', category } = {}) => {
                const urlParams = new URLSearchParams();
                urlParams.append("offset", ((page - 1) * 9).toString())
                urlParams.append("limit", '9')

                if (category) {
                    urlParams.set('categoryId', category.toString())
                } else {
                    urlParams.delete('categoryId')
                }


                if (rangeFilter.price_min && rangeFilter.price_max) {
                    urlParams.set('price_max', rangeFilter.price_max.toString());
                    urlParams.set('price_min', rangeFilter.price_min.toString());
                } else {
                    urlParams.delete('price_min');
                    urlParams.delete('price_max');
                }


                if (search) {
                    urlParams.set('title', search);
                } else {
                    urlParams.delete('title');
                }


                return `/products?${urlParams.toString()}`
            },
            providesTags: ['products']
        }),
        getAllProducts: builder.query<IData[], { rangeFilter?: TFilters, search?: string, category?: number } | void>({
            query: ({ rangeFilter = { price_min: null, price_max: null }, search, category } = {}) => {
                const urlParams = new URLSearchParams();

                if (category) {
                    urlParams.set('categoryId', category.toString())
                } else {
                    urlParams.delete('categoryId')
                }

                if (rangeFilter.price_min && rangeFilter.price_max) {
                    urlParams.set('price_max', rangeFilter.price_max.toString());
                    urlParams.set('price_min', rangeFilter.price_min.toString());
                } else {
                    urlParams.delete('price_min');
                    urlParams.delete('price_max');
                }

                if (search) {
                    urlParams.set('title', search);
                } else {
                    urlParams.delete('title');
                }
                return `/products?${urlParams.toString()}`
            },
            providesTags: ['products']
        }),
        getProduct: builder.query<IData, number | void>({
            query: (id) => `/products/${id}`,
        }),
    })
})

export const { useGetProductsQuery, useGetAllProductsQuery, useGetProductQuery } = productsApi;