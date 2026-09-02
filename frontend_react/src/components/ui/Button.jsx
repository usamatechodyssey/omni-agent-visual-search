import React from 'react'

const Button = ({
  children,
  variant = 'primary', // primary | secondary | danger | ghost
  size = 'md', // sm | md | lg
  isLoading = false,
  disabled = false,
  type = 'button',
  onClick,
  className = '',
  ...props
}) => {
  // Base classes
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-md transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-900 disabled:opacity-50 disabled:cursor-not-allowed'

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-xs',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  // Variant classes (using existing CSS utilities)
  const variantClasses = {
    primary: 'btn-primary text-white shadow-lg',
    secondary: 'border border-slate-600 text-slate-300 hover:bg-slate-800',
    danger: 'bg-red-500/10 text-red-400 hover:bg-red-500/20 border border-red-500/20',
    ghost: 'text-slate-400 hover:text-white',
  }

  const classes = `${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || isLoading}
      className={classes}
      {...props}
    >
      {isLoading ? (
        <svg className="animate-spin h-4 w-4 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : null}
      {children}
    </button>
  )
}

export default Button