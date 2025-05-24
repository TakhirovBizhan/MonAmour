import { useState } from 'react';
import { Painting } from '../../config/DataInterfaces';
import { getProducts } from './getProducts';

export const useProducts = () => {
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState<Painting[] | null>(null)
    const [error, setError] = useState<string[] | null>(null)

    setLoading(true);
    getProducts()
        .then((data) => {
            setData(data)
        })
        .catch((error) => {
            setError(error as string[])
        })
        .finally(() => setLoading(false))

    return { data, loading, error };
};