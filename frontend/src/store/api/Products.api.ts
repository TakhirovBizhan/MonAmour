import { IPaintingData, TFilters } from "../../config/DataInterfaces";
import { api } from "./api";


export const productsApi = api.injectEndpoints({
    endpoints: builder => ({
        getProducts: builder.query<IPaintingData, { page?: number, rangeFilter?: TFilters, search?: string, category?: number } | void>({
            query: ({ page = 0, rangeFilter = { price_min: null, price_max: null }, search = '', category } = {}) => {
                const urlParams = new URLSearchParams();
                urlParams.append("offset", ((page - 1) * 9).toString())
                urlParams.append("limit", '9')

                if (category) {
                    urlParams.set('category', category.toString())
                } else {
                    urlParams.delete('category')
                }


                if (rangeFilter.price_min && rangeFilter.price_max) {
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


                return `/paintings?${urlParams.toString()}`
            },
            providesTags: ['paintings']
        })
    })
})

export const { useGetProductsQuery } = productsApi;