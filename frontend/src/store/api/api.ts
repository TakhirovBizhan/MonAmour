import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const API_URL = 'https://api.escuelajs.co/api/v1';

export const api = createApi({
    reducerPath: 'api',
    tagTypes: ['products', 'categories', 'auth'],
    baseQuery: fetchBaseQuery({
        baseUrl: API_URL,
    }),
    endpoints: () => ({})
})