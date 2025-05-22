import { ICategory } from "../../config/DataInterfaces";
import { api } from "./api";

export const categoriesApi = api.injectEndpoints({
    endpoints: builder => ({

        getCategories: builder.query<ICategory[], void>({
            query: () => `/categories`,
            providesTags: ['categories']
        }),
        getCategory: builder.query<ICategory, number | void>({
            query: (id) => `/categories/${id}`,
        }),
    })
})

export const { useGetCategoriesQuery, useGetCategoryQuery } = categoriesApi;