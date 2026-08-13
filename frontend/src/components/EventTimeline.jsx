import React from 'react';

const EventTimeline = ({ events }) => {
  if (!events || events.length === 0) {
    return <p>No events recorded.</p>;
  }

  const getBadgeColor = (type) => {
    switch(type) {
      case 'created': return 'badge-success';
      case 'updated': return 'badge-info';
      case 'deleted': return 'badge-danger';
      case 'price_changed': return 'badge-warning';
      case 'stock_updated': return 'badge-info';
      default: return 'badge-secondary';
    }
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

  return (
    <div className="timeline">
      {events.map((event, index) => (
        <div key={index} className="timeline-item">
          <div className="timeline-dot" style={{ backgroundColor: `var(--${getBadgeColor(event.event_type).split('-')[1]})` }}></div>
          <div className="timeline-content">
            <div className="timeline-header">
              <span className={`badge ${getBadgeColor(event.event_type)}`}>
                {event.event_type}
              </span>
              <span className="timeline-date">{formatDate(event.timestamp)}</span>
            </div>
            
            {event.metadata && Object.keys(event.metadata).length > 0 && (
              <div className="metadata-grid">
                {Object.entries(event.metadata).map(([key, value]) => (
                  <React.Fragment key={key}>
                    <div className="metadata-key">{key}:</div>
                    <div className="metadata-value">{JSON.stringify(value)}</div>
                  </React.Fragment>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default EventTimeline;
