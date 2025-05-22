import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { IData } from '../config/DataInterfaces';

export interface CartState {
    data: IData[];
    fullPrice: number;
}

const defaultState: CartState = {
    data: [],
    fullPrice: 0,
};

const loadState = (): CartState => {
    try {
        const serializedState = localStorage.getItem('cartState');
        return serializedState ? JSON.parse(serializedState) : defaultState;
    } catch (e) {
        console.warn('Failed to load state from localStorage', e);
        return defaultState;
    }
};

const initialState: CartState = loadState();

export const productUrlSlice = createSlice({
    name: 'cart',
    initialState,
    reducers: {
        addToCart: (state, action: PayloadAction<IData>) => {
            state.data.push(action.payload);
            state.fullPrice = state.data.reduce((sum, item) => sum + item.price, 0);
        },
        removeFromCart: (state, action: PayloadAction<number>) => {
            const index = state.data.findIndex((item) => item.id === action.payload);
            if (index !== -1) {
                state.data.splice(index, 1);
            }
            state.fullPrice = state.data.reduce((sum, item) => sum + item.price, 0);
        },
        getFullPrice: (state) => {
            state.fullPrice = state.data.reduce((sum, item) => sum + item.price, 0);
        },
        clearCart: (state) => {
            state.data = [];
            state.fullPrice = 0;
        },
    },
});

export const { addToCart, removeFromCart, getFullPrice, clearCart } = productUrlSlice.actions;
export default productUrlSlice.reducer;

// Функция сохранения состояния корзины в localStorage
export const saveCartState = (state: CartState) => {
    try {
        const serializedState = JSON.stringify(state);
        localStorage.setItem('cartState', serializedState);
    } catch (e) {
        console.warn('Failed to save state to localStorage', e);
    }
};