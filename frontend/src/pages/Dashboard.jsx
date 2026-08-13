import { useProducts } from '../hooks/useProducts';
import { useOrders } from '../hooks/useOrders';
import LoadingSpinner from '../components/LoadingSpinner';

const STATUS_COLOR = {
  up: '#22c55e',
  down: '#ef4444',
  unknown: '#94a3b8',
};

const DbIndicator = ({ name, status }) => {
  const color = STATUS_COLOR[status] || STATUS_COLOR.unknown;
  return (
    <div className="db-indicator">
      <span className="status-dot" style={{ background: color }} />
      <span className="db-name">{name}</span>
      <span className="db-status" style={{ color }}>{status || 'unknown'}</span>
    </div>
  );
};

const Dashboard = ({ dbStatus }) => {
  const { products, loading: productsLoading } = useProducts();
  const { orders, loading: ordersLoading } = useOrders();

  if (productsLoading || ordersLoading) return <LoadingSpinner />;

  const recentProducts = [...products].sort((a, b) => b.id - a.id).slice(0, 5);
  const categoryCount = new Set(products.map((p) => p.category_id).filter(Boolean)).size;

  const deps = dbStatus?.status || {};

  return (
    <div>
      <h1>Dashboard</h1>

      {/* Stats Row */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <span className="stat-title">Total Products</span>
          <span className="stat-value">{products.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Total Orders</span>
          <span className="stat-value">{orders.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">Active Categories</span>
          <span className="stat-value">{categoryCount}</span>
        </div>
        <div className="stat-card">
          <span className="stat-title">DB Status</span>
          <span className="stat-value" style={{ fontSize: '1.2rem' }}>
            {dbStatus?.ready ? '✅ Ready' : '⚠️ Check'}
          </span>
        </div>
      </div>

      {/* DB Health */}
      <div className="card">
        <h2>Database Health</h2>
        <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.9rem' }}>
          Live connectivity status for all 4 databases. Refreshed every 30 seconds.
        </p>
        <div className="db-health-grid">
          <DbIndicator name="PostgreSQL" status={deps.postgres} />
          <DbIndicator name="MySQL" status={deps.mysql} />
          <DbIndicator name="MongoDB" status={deps.mongodb} />
          <DbIndicator name="Redis" status={deps.redis} />
        </div>
      </div>

      {/* Architecture */}
      <div className="card">
        <h2>System Architecture</h2>
        <p style={{ marginBottom: '0.75rem' }}>
          This application demonstrates <strong>polyglot persistence</strong> — using 4 databases,
          each optimised for its specific workload.
        </p>
        <div className="arch-grid">
          <div className="arch-item arch-pg">
            <strong>PostgreSQL</strong>
            <span>Core product catalog, categories &amp; suppliers — ACID, FK constraints</span>
          </div>
          <div className="arch-item arch-my">
            <strong>MySQL</strong>
            <span>Orders &amp; sales — transactional reporting, aggregation</span>
          </div>
          <div className="arch-item arch-mg">
            <strong>MongoDB</strong>
            <span>Product event history — flexible schema, append-only log</span>
          </div>
          <div className="arch-item arch-rd">
            <strong>Redis</strong>
            <span>Read cache — sub-ms reads, TTL-based invalidation</span>
          </div>
        </div>
      </div>

      {/* Recent Products */}
      <div className="card">
        <h2>Recent Products</h2>
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
              </tr>
            </thead>
            <tbody>
              {recentProducts.map((product) => (
                <tr key={product.id}>
                  <td>{product.id}</td>
                  <td>{product.name}</td>
                  <td><code>{product.sku}</code></td>
                  <td>{product.category_name || '—'}</td>
                  <td>${Number(product.price).toFixed(2)}</td>
                  <td>{product.stock}</td>
                </tr>
              ))}
              {recentProducts.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', color: '#94a3b8' }}>
                    No products yet. <a href="/products/new">Add one →</a>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
