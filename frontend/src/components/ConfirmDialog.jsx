const ConfirmDialog = ({ message, onConfirm, onCancel }) => {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <h3>Confirm Action</h3>
        <p className="mt-4">{message}</p>
        <div className="modal-actions">
          <button onClick={onCancel} className="btn btn-secondary">Cancel</button>
          <button onClick={onConfirm} className="btn btn-danger">Confirm</button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;
