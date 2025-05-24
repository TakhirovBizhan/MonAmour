import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const API_URL = 'http://localhost:8000/api';

export const api = createApi({
    reducerPath: 'api',
    tagTypes: ['paintings', 'categories', 'auth'],
    baseQuery: fetchBaseQuery({
        baseUrl: API_URL,
    }),
    endpoints: () => ({})
})