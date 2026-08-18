import { useState, useEffect } from 'react';
import { getCart, clearCart, startCheckout } from '../services/api';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

const Cart = ({ showToast }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  const fetchCart = async () => {
    try {
      const res = await getCart();
      setCart(res.data);
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to fetch cart', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  const handleClear = async () => {
    try {
      await clearCart();
      showToast('Cart cleared');
      fetchCart();
    } catch (err) {
      showToast('Failed to clear cart', 'error');
    }
  };

  const handleCheckout = async () => {
    setProcessing(true);
    try {
      await startCheckout();
      navigate('/checkout');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Checkout failed', 'error');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1>Your Cart</h1>
        {cart?.items?.length > 0 && (
          <button onClick={handleClear} className="btn btn-secondary">
            Clear Cart
          </button>
        )}
      </div>

      <div className="card">
        {!cart?.items?.length ? (
          <p style={{ textAlign: 'center' }}>Your cart is empty.</p>
        ) : (
          <div>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Price</th>
                    <th>Qty</th>
                    <th>Subtotal</th>
                  </tr>
                </thead>
                <tbody>
                  {cart.items.map((item, idx) => (
                    <tr key={idx}>
                      <td>{item.product_name}</td>
                      <td>${item.unit_price.toFixed(2)}</td>
                      <td>{item.quantity}</td>
                      <td>${(item.unit_price * item.quantity).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            <div style={{ marginTop: '20px', textAlign: 'right' }}>
              <h3>Total: ${cart.total_amount.toFixed(2)}</h3>
              <button 
                className="btn btn-primary mt-4" 
                onClick={handleCheckout}
                disabled={processing}
              >
                {processing ? 'Processing...' : 'Proceed to Checkout'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Cart;
