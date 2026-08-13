import { useState, useEffect, useCallback } from 'react';
import { getProducts, deleteProduct } from '../services/api';

export const useProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getProducts();
      setProducts(response.data.items || response.data);
    } catch (err) {
      setError(err.message || 'Failed to fetch products');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const removeProduct = async (id) => {
    try {
      await deleteProduct(id);
      setProducts(prev => prev.filter(p => p.id !== id));
      return true;
    } catch (err) {
      setError(err.message || 'Failed to delete product');
      return false;
    }
  };

  return { products, loading, error, fetchProducts, removeProduct };
};
