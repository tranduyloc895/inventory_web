import { NavLink } from 'react-router-dom';

const Navbar = ({ dbStatus }) => {
  const renderDbStatus = () => {
    if (!dbStatus) return <p className="db-status-item">Loading status...</p>;
    
    // Fallback if status format is different, adapt as needed
    const dbs = [
      { name: 'PostgreSQL', key: 'postgresql' },
      { name: 'MySQL', key: 'mysql' },
      { name: 'MongoDB', key: 'mongodb' },
      { name: 'Redis', key: 'redis' }
    ];

    return dbs.map(db => {
      // Check if healthy, default false
      const isHealthy = dbStatus[db.key]?.status === 'ok' || dbStatus[db.key] === 'ok' || dbStatus[db.key] === true;
      return (
        <div key={db.key} className="db-status-item">
          <span className={`status-dot ${isHealthy ? 'green' : 'red'}`}></span>
          {db.name}
        </div>
      );
    });
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-header">
        <h2>Polyglot Inventory</h2>
        <p>4-Database Demo</p>
      </div>
      
      <ul className="nav-links">
        <li>
          <NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>
            📊 Dashboard
          </NavLink>
        </li>
        <li>
          <NavLink to="/products" className={({ isActive }) => (isActive ? 'active' : '')}>
            📦 Products
          </NavLink>
        </li>
        <li>
          <NavLink to="/orders" className={({ isActive }) => (isActive ? 'active' : '')}>
            🛒 Orders
          </NavLink>
        </li>
      </ul>

      <div className="sidebar-footer">
        <h3 style={{ fontSize: '0.875rem', marginBottom: '0.5rem', color: '#fff' }}>DB Health</h3>
        {renderDbStatus()}
      </div>
    </nav>
  );
};

export default Navbar;
