import { useState } from 'react';
import { useOrders } from '../hooks/useOrders';
import { createOrder, updateOrderStatus } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../hooks/useAuth';

const OrderList = ({ showToast }) => {
  const { orders, loading, error, fetchOrders } = useOrders();
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [formData, setFormData] = useState({
    product_id: '',
    quantity: 1,
    notes: ''
  });

  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'badge-success';
      case 'pending': return 'badge-warning';
      case 'cancelled': return 'badge-danger';
      default: return 'badge-secondary';
    }
  };

  const handleUpdateStatus = async (orderId, newStatus) => {
    try {
      await updateOrderStatus(orderId, newStatus);
      showToast('Order status updated');
      fetchOrders();
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to update status', 'error');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.product_id || formData.quantity < 1) {
      showToast('Please provide valid product ID and quantity', 'error');
      return;
    }

    setCreating(true);
    try {
      const payload = {
        notes: formData.notes,
        items: [
          {
            product_id: parseInt(formData.product_id, 10),
            quantity: parseInt(formData.quantity, 10)
          }
        ]
      };
      await createOrder(payload);
      showToast('Order created successfully');
      setShowModal(false);
      fetchOrders();
      setFormData({ product_id: '', quantity: 1, notes: '' });
    } catch (err) {
      showToast(err.response?.data?.detail || 'Failed to create order', 'error');
    } finally {
      setCreating(false);
    }
  };

  if (loading && !showModal) return <LoadingSpinner />;
  if (error) return <div className="card"><p className="form-error">{error}</p></div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1>Orders</h1>
        {user?.role !== 'admin' && (
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            + Create Order
          </button>
        )}
      </div>

      <div className="card">
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Order ID</th>
                {user?.role === 'admin' && <th>User ID</th>}
                <th>Date</th>
                <th>Status</th>
                <th>Total Amount</th>
                <th>Items Count</th>
                <th>Notes</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(order => (
                <tr key={order.id}>
                  <td>#{order.id}</td>
                  {user?.role === 'admin' && <td>{order.user_id}</td>}
                  <td>{new Date(order.created_at).toLocaleString()}</td>
                  <td>
                    <span className={`badge ${getStatusBadge(order.status)}`}>
                      {order.status || 'Pending'}
                    </span>
                  </td>
                  <td>${(order.total_amount || 0).toFixed(2)}</td>
                  <td>{order.items?.length || 0}</td>
                  <td>{order.notes || '-'}</td>
                  <td>
                    {order.can_process && order.status !== 'completed' ? (
                      <button 
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleUpdateStatus(order.id, 'completed')}
                      >
                        Complete
                      </button>
                    ) : (
                      <button 
                        className="btn btn-outline-secondary btn-sm"
                        onClick={() => showToast('Order details view is under construction', 'info')}
                      >
                        View
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {orders.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center' }}>No orders found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Create New Order</h3>
            <form onSubmit={handleSubmit} className="mt-4">
              <div className="form-group">
                <label className="form-label">Product ID *</label>
                <input
                  type="number"
                  className="form-control"
                  value={formData.product_id}
                  onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Quantity *</label>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={formData.quantity}
                  onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label className="form-label">Notes</label>
                <textarea
                  className="form-control"
                  rows="2"
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                ></textarea>
              </div>
              <div className="modal-actions">
                <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" disabled={creating}>
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderList;
