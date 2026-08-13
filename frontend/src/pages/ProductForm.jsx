import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getProduct, createProduct, updateProduct, getCategories } from '../services/api';
import LoadingSpinner from '../components/LoadingSpinner';

const ProductForm = ({ showToast }) => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [loading, setLoading] = useState(isEdit);
  const [saving, setSaving] = useState(false);
  const [categories, setCategories] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    supplier_id: '',
  });
  const [errors, setErrors] = useState({});

  // Fetch categories for dropdown
  useEffect(() => {
    getCategories()
      .then((res) => setCategories(res.data || []))
      .catch(() => setCategories([]));
  }, []);

  // Load product data when editing
  useEffect(() => {
    if (!isEdit) return;
    const fetchProduct = async () => {
      try {
        const res = await getProduct(id);
        const p = res.data;
        setFormData({
          name: p.name || '',
          sku: p.sku || '',
          description: p.description || '',
          price: p.price ?? '',
          stock: p.stock ?? '',
          category_id: p.category_id ?? '',
          supplier_id: p.supplier_id ?? '',
        });
      } catch {
        showToast('Failed to load product', 'error');
        navigate('/products');
      } finally {
        setLoading(false);
      }
    };
    fetchProduct();
  }, [id, isEdit, navigate, showToast]);

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.sku.trim()) newErrors.sku = 'SKU is required';
    if (formData.price === '' || Number(formData.price) < 0)
      newErrors.price = 'Valid price (≥ 0) is required';
    if (formData.stock === '' || Number(formData.stock) < 0)
      newErrors.stock = 'Valid stock (≥ 0) is required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setSaving(true);
    try {
      const payload = {
        name: formData.name.trim(),
        sku: formData.sku.trim(),
        description: formData.description.trim() || null,
        price: Number(formData.price),
        stock: parseInt(formData.stock, 10),
        category_id: formData.category_id ? parseInt(formData.category_id, 10) : null,
        supplier_id: formData.supplier_id ? parseInt(formData.supplier_id, 10) : null,
      };

      if (isEdit) {
        await updateProduct(id, payload);
        showToast('Product updated successfully');
      } else {
        await createProduct(payload);
        showToast('Product created successfully');
      }
      navigate('/products');
    } catch (err) {
      const detail = err.response?.data?.detail;
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(', ')
        : detail || 'Failed to save product';
      showToast(msg, 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner />;

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto' }}>
      <h1>{isEdit ? 'Edit Product' : 'New Product'}</h1>

      <div className="card">
        <form onSubmit={handleSubmit}>
          {/* Name */}
          <div className="form-group">
            <label className="form-label">Name *</label>
            <input
              type="text"
              name="name"
              className="form-control"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Wireless Mouse"
            />
            {errors.name && <div className="form-error">{errors.name}</div>}
          </div>

          {/* SKU */}
          <div className="form-group">
            <label className="form-label">SKU *</label>
            <input
              type="text"
              name="sku"
              className="form-control"
              value={formData.sku}
              onChange={handleChange}
              placeholder="e.g. ELEC-WM-001"
            />
            {errors.sku && <div className="form-error">{errors.sku}</div>}
          </div>

          {/* Category */}
          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              name="category_id"
              className="form-control"
              value={formData.category_id}
              onChange={handleChange}
            >
              <option value="">— No category —</option>
              {categories.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Price + Stock */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Price (USD) *</label>
              <input
                type="number"
                step="0.01"
                min="0"
                name="price"
                className="form-control"
                value={formData.price}
                onChange={handleChange}
                placeholder="0.00"
              />
              {errors.price && <div className="form-error">{errors.price}</div>}
            </div>

            <div className="form-group">
              <label className="form-label">Stock *</label>
              <input
                type="number"
                min="0"
                name="stock"
                className="form-control"
                value={formData.stock}
                onChange={handleChange}
                placeholder="0"
              />
              {errors.stock && <div className="form-error">{errors.stock}</div>}
            </div>
          </div>

          {/* Supplier ID (optional) */}
          <div className="form-group">
            <label className="form-label">Supplier ID (optional)</label>
            <input
              type="number"
              min="1"
              name="supplier_id"
              className="form-control"
              value={formData.supplier_id}
              onChange={handleChange}
              placeholder="Leave blank if unknown"
            />
          </div>

          {/* Description */}
          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              name="description"
              className="form-control"
              rows="3"
              value={formData.description}
              onChange={handleChange}
              placeholder="Optional product description…"
            />
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1rem' }}>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving…' : isEdit ? 'Update Product' : 'Create Product'}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate('/products')}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProductForm;
