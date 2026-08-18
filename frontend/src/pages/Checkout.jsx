import { useState, useEffect } from 'react';
import { getCheckoutSession, completeCheckout } from '../services/api';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';

const Checkout = ({ showToast }) => {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await getCheckoutSession();
        setSession(res.data);
      } catch (err) {
        showToast(err.response?.data?.detail || 'No active checkout session', 'error');
        navigate('/cart');
      } finally {
        setLoading(false);
      }
    };
    fetchSession();
  }, [navigate, showToast]);

  const handleConfirm = async () => {
    setProcessing(true);
    try {
      await completeCheckout();
      showToast('Order confirmed successfully!', 'success');
      navigate('/orders');
    } catch (err) {
      showToast(err.response?.data?.detail || 'Checkout failed', 'error');
      setProcessing(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!session) return null;

  return (
    <div>
      <h1 className="mb-4">Checkout</h1>
      <div className="card">
        <h2>Order Summary</h2>
        <div style={{ margin: '20px 0' }}>
          {session.cart.items.map((item, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #eee' }}>
              <span>{item.quantity}x {item.product_name}</span>
              <span>${(item.quantity * item.unit_price).toFixed(2)}</span>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 0', fontWeight: 'bold', fontSize: '1.2rem' }}>
            <span>Total</span>
            <span>${session.cart.total_amount.toFixed(2)}</span>
          </div>
        </div>
        
        <div style={{ marginTop: '30px' }}>
          <p style={{ color: '#666', marginBottom: '15px' }}>By confirming, this checkout session (Redis) will be converted to an Order (PostgreSQL) and the Cart (MongoDB) will be cleared.</p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button 
              className="btn btn-secondary" 
              onClick={() => navigate('/cart')}
              disabled={processing}
            >
              Back to Cart
            </button>
            <button 
              className="btn btn-primary" 
              onClick={handleConfirm}
              disabled={processing}
            >
              {processing ? 'Confirming...' : 'Confirm Order'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
