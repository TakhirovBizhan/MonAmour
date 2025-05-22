import { useState } from 'react';
import { IData } from '../../config/DataInterfaces';
import { getProducts } from './getProduct';

export const useProducts = (id: string) => {
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<IData | null>(null)
    const [error, setError] = useState<string[] | null>(null)

    setLoading(true);
    getProducts(id)
        .then((data) => {
            setData(data)
        })
        .catch((error) => {
            setError(error as string[])
        })
        .finally(() => setLoading(false))

    return { data, loading, error };
};