import axios from "axios";
import { IData } from "../../config/DataInterfaces";
import { ErrorHandler } from "../../utils/ErrorHandler";

export const getProducts = async (offset: number = 0, limit: number = 10) => {
    try {
        const response = await axios.get<IData[]>(`https://api.escuelajs.co/api/v1/products?offset=${offset}&limit=${limit}`);
        return response.data;
    } catch (error) {
        const errorMessages = await ErrorHandler.getErrors(error);
        console.error(errorMessages);
        throw errorMessages;
    }
};