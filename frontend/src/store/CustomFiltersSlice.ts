import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { Painting } from '../config/DataInterfaces';

export interface CustomFilterState {
    order: 'asc' | 'desc' | null,
    filteredData: Painting[] | null
}

const initialState: CustomFilterState = {
    order: null,
    filteredData: []
};

export const CustomFilterSlice = createSlice({
    name: 'customFilter',
    initialState,
    reducers: {
        setData: (state, action: PayloadAction<Painting[]>) => {
            state.filteredData = action.payload;
        },

        setOrder: (state, action: PayloadAction<'asc' | 'desc' | null>) => {
            state.order = action.payload
            if (state.filteredData) {
                state.filteredData = state.filteredData.toSorted((a, b) =>
                    state.order === 'asc' ? a.price - b.price : b.price - a.price
                );
            }
        },
    },
});

export const { setOrder, setData } = CustomFilterSlice.actions;
export default CustomFilterSlice.reducer;