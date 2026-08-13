const Toast = ({ message, type = 'success', onClose }) => {
  return (
    <div className="toast-container">
      <div className={`toast toast-${type}`}>
        <span>{message}</span>
        <button 
          onClick={onClose}
          style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '1.2rem' }}
        >
          &times;
        </button>
      </div>
    </div>
  );
};

export default Toast;
