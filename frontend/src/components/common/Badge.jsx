import { forwardRef } from 'react';

/**
 * Reusable Badge component for status indicators and labels.
 */
const Badge = forwardRef(
  (
    {
      children,
      variant = 'default',
      size = 'md',
      dot = false,
      className = '',
      ...props
    },
    ref
  ) => {
    const baseClasses = 'badge';

    const variantClasses = {
      default: 'badge-default',
      primary: 'badge-primary',
      success: 'badge-success',
      warning: 'badge-warning',
      error: 'badge-error',
      info: 'badge-info',
    };

    const sizeClasses = {
      sm: 'badge-sm',
      md: 'badge-md',
      lg: 'badge-lg',
    };

    const dotClass = {
      success: 'badge-dot success',
      warning: 'badge-dot warning',
      error: 'badge-dot error',
      default: 'badge-dot accent',
      primary: 'badge-dot accent',
      info: 'badge-dot accent',
    };

    return (
      <span
        ref={ref}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...props}
      >
        {dot && <span className={dotClass[variant]} />}
        {children}
      </span>
    );
  }
);

Badge.displayName = 'Badge';

export default Badge;