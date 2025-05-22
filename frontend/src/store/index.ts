import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { api } from "./api/api";
import ProductUrlSlice from "./ProductUrlSlice";
import cartSlice, { saveCartState } from "./CartSlice";

const reducers = combineReducers({
    [api.reducerPath]: api.reducer,
    productUrl: ProductUrlSlice,
    cart: cartSlice
})

export const store = configureStore({
    reducer: reducers,
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware().concat(api.middleware),
})

store.subscribe(() => {
    const state = store.getState();
    saveCartState(state.cart);
});


export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch