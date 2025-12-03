import React from 'react'
import clsx from 'clsx'

const Card = ({ 
  children, 
  className, 
  padding = true, 
  shadow = true, 
  hover = false,
  ...props 
}) => {
  return (
    <div
      className={clsx(
        'bg-white rounded-lg border border-gray-200',
        {
          'p-6': padding,
          'shadow-sm': shadow && !hover,
          'shadow-sm hover:shadow-md transition-shadow duration-200': shadow && hover,
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

const CardHeader = ({ children, className, ...props }) => {
  return (
    <div
      className={clsx('px-6 py-4 border-b border-gray-200', className)}
      {...props}
    >
      {children}
    </div>
  )
}

const CardBody = ({ children, className, ...props }) => {
  return (
    <div
      className={clsx('px-6 py-4', className)}
      {...props}
    >
      {children}
    </div>
  )
}

const CardFooter = ({ children, className, ...props }) => {
  return (
    <div
      className={clsx('px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-lg', className)}
      {...props}
    >
      {children}
    </div>
  )
}

Card.Header = CardHeader
Card.Body = CardBody
Card.Footer = CardFooter

export default Card