import axios from 'axios';

export class ErrorHandler {
    static async getErrors(error: unknown): Promise<string[]> {
        let errorMessages: string[] = [];

        if (axios.isAxiosError(error)) {
            if (error?.response) {
                errorMessages = [`Ошибка ${error.response.status}: ${error.response.data}`];
            } else if (error?.request) {
                errorMessages = [`Нет ответа от сервера`];
            } else {
                errorMessages = [`Ошибка при настройке запроса: ${error.message}`];
            }
        } else {
            errorMessages = [`Неизвестная ошибка: ${error}`];
        }

        return errorMessages;
    }
}
