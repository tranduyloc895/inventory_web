import { Link } from 'react-router-dom';

const ProductCard = ({ product, onDelete }) => {
  return (
    <div className="card">
      <h3>{product.name}</h3>
      <p className="mb-4 text-sm text-gray-500">SKU: {product.sku}</p>
      
      <div className="flex-between mb-4">
        <span className="font-bold text-lg">${product.price.toFixed(2)}</span>
        <span className={`badge ${product.stock < 10 ? 'badge-danger' : product.stock < 50 ? 'badge-warning' : 'badge-success'}`}>
          Stock: {product.stock}
        </span>
      </div>
      
      <div className="flex-between mt-4 border-t pt-4">
        <Link to={`/products/${product.id}`} className="btn btn-secondary btn-sm">
          View Details
        </Link>
        <div className="flex gap-2">
          <Link to={`/products/${product.id}/edit`} className="btn btn-primary btn-sm">
            Edit
          </Link>
          <button onClick={() => onDelete(product.id)} className="btn btn-danger btn-sm">
            Delete
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
