import { forwardRef } from 'react';

/**
 * Reusable Card component with glassmorphism styling.
 */
const Card = forwardRef(
  (
    {
      children,
      title,
      titleIcon: TitleIcon,
      headerAction,
      className = '',
      bodyClassName = '',
      headerClassName = '',
      noPadding = false,
      ...props
    },
    ref
  ) => {
    return (
      <div
        ref={ref}
        className={`surface-card ${className}`}
        {...props}
      >
        {(title || headerAction) && (
          <div
            className={`card-header ${headerClassName}`}
          >
            {title && (
              <div className="card-title">
                {TitleIcon && <TitleIcon size={18} />}
                <h3>{title}</h3>
              </div>
            )}
            {headerAction}
          </div>
        )}
        <div className={`${noPadding ? 'card-body no-padding' : 'card-body'} ${bodyClassName}`}>
          {children}
        </div>
      </div>
    );
  }
);

Card.displayName = 'Card';

export default Card;