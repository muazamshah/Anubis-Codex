import { forwardRef } from 'react';

/**
 * Reusable Button component with multiple variants.
 */
const Button = forwardRef(
  (
    {
      children,
      variant = 'primary',
      size = 'md',
      icon: Icon,
      iconPosition = 'left',
      loading = false,
      disabled = false,
      className = '',
      onClick,
      ...props
    },
    ref
  ) => {
    const baseClasses = 'btn';

    const variantClasses = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
      ghost: 'btn-ghost',
      danger: 'btn-danger',
      success: 'btn-success',
    };

    const sizeClasses = {
      sm: 'btn-sm',
      md: 'btn-md',
      lg: 'btn-lg',
    };

    const iconSizes = {
      sm: 14,
      md: 16,
      lg: 18,
    };

    const handleClick = (e) => {
      if (disabled || loading) return;
      if (onClick) onClick(e);
    };

    return (
      <button
        ref={ref}
        onClick={handleClick}
        disabled={disabled || loading}
        className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
        {...props}
      >
        {loading && <span className="btn-spinner" />}
        {Icon && !loading && iconPosition === 'left' && (
          <Icon size={iconSizes[size]} style={{ marginRight: '0.5rem' }} />
        )}
        {children}
        {Icon && !loading && iconPosition === 'right' && (
          <Icon size={iconSizes[size]} style={{ marginLeft: '0.5rem' }} />
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;