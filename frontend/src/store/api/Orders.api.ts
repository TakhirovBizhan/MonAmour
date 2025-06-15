// store/api/Orders.api.ts
import { api } from './api';  // ваш базовый api
import { PostOrder, OrderResponse } from '../../config/DataInterfaces';

export const OrdersApi = api.injectEndpoints({
    endpoints: (builder) => ({
        // Запрос списка заказов текущего пользователя
        getOrders: builder.query<OrderResponse[], void>({
            // Предполагаем, что бэкенд поддерживает фильтрацию по ?user=<id>
            query: () => {
                const userId = localStorage.getItem('currentUser');
                // Если backend не требует параметра user (берёт из токена), уберите параметр
                return `/orders/?user=${userId}`;
            },
        }),

        // Мутация: создание заказа
        postOrder: builder.mutation<OrderResponse, PostOrder>({
            query: (orderData) => ({
                url: '/orders/',
                method: 'POST',
                body: orderData,
            }),
            // после создания заказа перезапросим корзину и список заказов
        }),

        // (Опционально) Получить детали конкретного заказа
        getOrderById: builder.query<OrderResponse, string>({
            query: (orderId) => `/orders/${orderId}/`,
        }),
    }),
});

export const {
    useGetOrdersQuery,
    usePostOrderMutation,
    useGetOrderByIdQuery,
} = OrdersApi;