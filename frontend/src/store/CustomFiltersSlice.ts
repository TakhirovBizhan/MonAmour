import { createSlice } from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { IData } from '../config/DataInterfaces';

export interface CustomFilterState {
    order: 'asc' | 'desc' | null,
    filteredData: IData[] | null
}

const initialState: CustomFilterState = {
    order: null,
    filteredData: []
};

export const CustomFilterSlice = createSlice({
    name: 'customFilter',
    initialState,
    reducers: {
        setData: (state, action: PayloadAction<IData[]>) => {
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