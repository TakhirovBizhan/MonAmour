import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { TFilters } from '../config/DataInterfaces';

export interface ProductUrlState {
    page: number;
    rangeFilter: TFilters;
    search: string;
    gallery: string
}

const initialState: ProductUrlState = {
    page: 1,
    rangeFilter: { price_min: null, price_max: null },
    search: '',
    gallery: ''
};

export const productUrlSlice = createSlice({
    name: 'filter',
    initialState,
    reducers: {
        setPage: (state, action: PayloadAction<number>) => {
            state.page = action.payload;
        },
        incrementPage: (state) => {
            state.page = state.page + 1
        },
        decrementPage: (state) => {
            state.page = state.page - 1
        },
        setMinPrice: (state, action: PayloadAction<number | null>) => {
            state.rangeFilter.price_min = action.payload;
        },
        setMaxPrice: (state, action: PayloadAction<number | null>) => {
            state.rangeFilter.price_max = action.payload;
        },
        setSearch: (state, action: PayloadAction<string>) => {
            state.search = action.payload;
        },
        setGallery: (state, action: PayloadAction<string>) => {
            state.gallery = action.payload;
        },
    },
});

export const { setPage, setMinPrice, setMaxPrice, setSearch, incrementPage, decrementPage, setGallery } = productUrlSlice.actions;
export default productUrlSlice.reducer;