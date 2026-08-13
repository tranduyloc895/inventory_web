import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useProducts } from '../hooks/useProducts';
import LoadingSpinner from '../components/LoadingSpinner';
import ConfirmDialog from '../components/ConfirmDialog';

const ProductList = ({ showToast }) => {
  const { products, loading, error, removeProduct } = useProducts();
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteId, setDeleteId] = useState(null);

  const filteredProducts = useMemo(() => {
    return products.filter(p => 
      p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
      p.sku.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [products, searchTerm]);

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    const success = await removeProduct(deleteId);
    if (success) {
      showToast('Product deleted successfully');
    } else {
      showToast('Failed to delete product', 'error');
    }
    setDeleteId(null);
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="card"><p className="form-error">{error}</p></div>;

  return (
    <div>
      <div className="flex-between mb-4">
        <h1>Products</h1>
        <Link to="/products/new" className="btn btn-primary">
          + Add Product
        </Link>
      </div>

      <div className="card">
        <div className="mb-4">
          <input
            type="text"
            placeholder="Search by name or SKU..."
            className="form-control"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ maxWidth: '300px' }}
          />
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map(product => (
                <tr key={product.id}>
                  <td>{product.id}</td>
                  <td>{product.name}</td>
                  <td>{product.sku}</td>
                  <td>{product.category || 'N/A'}</td>
                  <td>${product.price.toFixed(2)}</td>
                  <td>
                    <span className={`badge ${product.stock < 10 ? 'badge-danger' : product.stock < 50 ? 'badge-warning' : 'badge-success'}`}>
                      {product.stock}
                    </span>
                  </td>
                  <td>
                    <div className="table-actions">
                      <Link to={`/products/${product.id}`} className="btn btn-secondary btn-sm">View</Link>
                      <Link to={`/products/${product.id}/edit`} className="btn btn-primary btn-sm">Edit</Link>
                      <button onClick={() => setDeleteId(product.id)} className="btn btn-danger btn-sm">Delete</button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredProducts.length === 0 && (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center' }}>No products found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {deleteId && (
        <ConfirmDialog
          message="Are you sure you want to delete this product? This action cannot be undone."
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteId(null)}
        />
      )}
    </div>
  );
};

export default ProductList;
