import { Category } from "../../config/DataInterfaces";
import { api } from "./api";

export const categoriesApi = api.injectEndpoints({
    endpoints: builder => ({

        getCategories: builder.query<Category[], void>({
            query: () => `/categories`,
            providesTags: ['categories']
        }),
        getCategory: builder.query<Category, string | void>({
            query: (id) => `/categories/${id}`,
        }),
    })
})

export const { useGetCategoriesQuery, useGetCategoryQuery } = categoriesApi;