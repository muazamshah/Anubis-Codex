import { forwardRef } from 'react';

/**
 * StatusIndicator - Shows a colored dot with a label for status display.
 */
const StatusIndicator = forwardRef(
  (
    {
      status = 'idle',
      label,
      size = 'md',
      showDot = true,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={`status-indicator ${className}`}
        {...props}
      >
        {showDot && (
          <span className={`status-dot ${size} ${status}`} />
        )}
        {label && <span className="status-label">{label}</span>}
      </div>
    );
  }
);

StatusIndicator.displayName = 'StatusIndicator';

export default StatusIndicator;