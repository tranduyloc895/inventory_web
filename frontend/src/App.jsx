import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import ProductList from './pages/ProductList';
import ProductForm from './pages/ProductForm';
import ProductDetail from './pages/ProductDetail';
import OrderList from './pages/OrderList';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import ProtectedRoute from './components/ProtectedRoute';
import Toast from './components/Toast';
import { useState, useEffect } from 'react';
import { getReadiness } from './services/api';

function App() {
  const [toast, setToast] = useState(null);
  const [dbStatus, setDbStatus] = useState(null);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await getReadiness();
        setDbStatus(res.data);
      } catch (err) {
        if (err.response && err.response.data) {
          setDbStatus(err.response.data);
        } else {
          console.error('Failed to fetch DB status', err);
        }
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-layout">
      <Navbar dbStatus={dbStatus} />
      <div className="main-content">
        <Routes>
          <Route path="/login" element={<Login showToast={showToast} />} />
          <Route path="/register" element={<Register showToast={showToast} />} />
          
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<Dashboard dbStatus={dbStatus} />} />
            <Route path="/products" element={<ProductList showToast={showToast} />} />
            <Route path="/products/new" element={<ProductForm showToast={showToast} />} />
            <Route path="/products/:id" element={<ProductDetail showToast={showToast} />} />
            <Route path="/products/:id/edit" element={<ProductForm showToast={showToast} />} />
            <Route path="/orders" element={<OrderList showToast={showToast} />} />
            <Route path="/cart" element={<Cart showToast={showToast} />} />
            <Route path="/checkout" element={<Checkout showToast={showToast} />} />
          </Route>
        </Routes>
        
        <footer className="app-footer">
          Polyglot Persistence Demo | PostgreSQL + MySQL + MongoDB + Redis
        </footer>
      </div>
      {toast && (
        <Toast 
          message={toast.message} 
          type={toast.type} 
          onClose={() => setToast(null)} 
        />
      )}
    </div>
  );
}

export default App;
