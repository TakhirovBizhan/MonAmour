import { useEffect, useState } from 'react';
import axios from 'axios';
import { IData } from '../config/DataInterfaces';

export const useProducts = () => {
  const [data, setData] = useState<IData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!loading) return;
        const result = await axios.get('https://api.escuelajs.co/api/v1/products');
        setData(result.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [loading]);

  return { data, loading };
};

export const useProduct = (id: string | undefined) => {
  const [data, setData] = useState<IData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await axios.get(`https://api.escuelajs.co/api/v1/products/${id}`);
        setData(result.data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  return { data, loading };
};
