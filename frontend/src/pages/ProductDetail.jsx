import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getProduct, getProductEvents, getProductSales, deleteProduct } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';
import EventTimeline from '../components/EventTimeline';
import ConfirmDialog from '../components/ConfirmDialog';

const ProductDetail = ({ showToast }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [product, setProduct] = useState(null);
  const [events, setEvents] = useState([]);
  const [sales, setSales] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('info');
  const [deleteDialog, setDeleteDialog] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [prodRes, eventsRes, salesRes] = await Promise.allSettled([
          getProduct(id),
          getProductEvents(id),
          getProductSales(id).catch(() => ({ data: { total_sold: 0, total_revenue: 0 } }))
        ]);

        if (prodRes.status === 'fulfilled') {
          setProduct(prodRes.value.data);
        } else {
          showToast('Failed to load product', 'error');
          navigate('/products');
        }

        if (eventsRes.status === 'fulfilled') {
          setEvents(eventsRes.value.data || []);
        }

        if (salesRes.status === 'fulfilled') {
          setSales(salesRes.value.data);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id, navigate, showToast]);

  const handleDelete = async () => {
    try {
      await deleteProduct(id);
      showToast('Product deleted successfully');
      navigate('/products');
    } catch (err) {
      showToast('Failed to delete product', 'error');
      setDeleteDialog(false);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (!product) return <div>Product not found</div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1>{product.name}</h1>
        <div className="flex gap-2">
          <Link to={`/products/${id}/edit`} className="btn btn-primary">Edit Product</Link>
          <button onClick={() => setDeleteDialog(true)} className="btn btn-danger">Delete</button>
        </div>
      </div>

      <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', gap: '1rem' }}>
        <button 
          className={`btn ${activeTab === 'info' ? 'btn-primary' : 'btn-secondary'}`} 
          style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
          onClick={() => setActiveTab('info')}
        >
          Product Info
        </button>
        <button 
          className={`btn ${activeTab === 'sales' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
          onClick={() => setActiveTab('sales')}
        >
          Sales Summary
        </button>
        <button 
          className={`btn ${activeTab === 'events' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
          onClick={() => setActiveTab('events')}
        >
          Event History
        </button>
      </div>

      {activeTab === 'info' && (
        <div className="card">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <p className="mb-4"><strong>SKU:</strong> {product.sku}</p>
              <p className="mb-4"><strong>Category:</strong> {product.category || 'N/A'}</p>
              <p className="mb-4"><strong>Description:</strong> {product.description || 'No description'}</p>
            </div>
            <div>
              <p className="mb-4">
                <strong>Price:</strong> <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>${product.price?.toFixed(2)}</span>
              </p>
              <p className="mb-4">
                <strong>Stock:</strong> 
                <span className={`badge ml-2 ${product.stock < 10 ? 'badge-danger' : product.stock < 50 ? 'badge-warning' : 'badge-success'}`}>
                  {product.stock}
                </span>
              </p>
              <p className="mb-4"><strong>Created:</strong> {new Date(product.created_at).toLocaleString()}</p>
              <p className="mb-4"><strong>Updated:</strong> {new Date(product.updated_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'sales' && (
        <div className="dashboard-stats">
          <div className="stat-card">
            <span className="stat-title">Total Units Sold</span>
            <span className="stat-value">{sales?.total_sold || 0}</span>
          </div>
          <div className="stat-card">
            <span className="stat-title">Total Revenue</span>
            <span className="stat-value">${(sales?.total_revenue || 0).toFixed(2)}</span>
          </div>
        </div>
      )}

      {activeTab === 'events' && (
        <div className="card">
          <h2>Event History (MongoDB)</h2>
          <EventTimeline events={events} />
        </div>
      )}

      {deleteDialog && (
        <ConfirmDialog
          message="Are you sure you want to delete this product?"
          onConfirm={handleDelete}
          onCancel={() => setDeleteDialog(false)}
        />
      )}
    </div>
  );
};

export default ProductDetail;
