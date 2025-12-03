import React, { forwardRef } from 'react'
import clsx from 'clsx'

const Input = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className, 
  type = 'text',
  required = false,
  ...props 
}, ref) => {
  return (
    <div className="mb-4">
      {label && (
        <label className={clsx('form-label', { 'required': required })}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        className={clsx(
          'form-input',
          {
            'border-red-300 focus:ring-red-500 focus:border-red-500': error,
          },
          className
        )}
        {...props}
      />
      {error && <p className="form-error">{error}</p>}
      {helperText && !error && <p className="text-gray-500 text-sm mt-1">{helperText}</p>}
    </div>
  )
})

Input.displayName = 'Input'

const TextArea = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className, 
  rows = 4,
  required = false,
  ...props 
}, ref) => {
  return (
    <div className="mb-4">
      {label && (
        <label className={clsx('form-label', { 'required': required })}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={clsx(
          'form-input',
          {
            'border-red-300 focus:ring-red-500 focus:border-red-500': error,
          },
          className
        )}
        {...props}
      />
      {error && <p className="form-error">{error}</p>}
      {helperText && !error && <p className="text-gray-500 text-sm mt-1">{helperText}</p>}
    </div>
  )
})

TextArea.displayName = 'TextArea'

const Select = forwardRef(({ 
  label, 
  error, 
  helperText, 
  className, 
  children,
  placeholder,
  required = false,
  ...props 
}, ref) => {
  return (
    <div className="mb-4">
      {label && (
        <label className={clsx('form-label', { 'required': required })}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <select
        ref={ref}
        className={clsx(
          'form-input',
          {
            'border-red-300 focus:ring-red-500 focus:border-red-500': error,
          },
          className
        )}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {children}
      </select>
      {error && <p className="form-error">{error}</p>}
      {helperText && !error && <p className="text-gray-500 text-sm mt-1">{helperText}</p>}
    </div>
  )
})

Select.displayName = 'Select'

Input.TextArea = TextArea
Input.Select = Select

export default Input