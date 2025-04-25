import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

const Button = ({
  children,
  to,
  href,
  onClick,
  type = 'button',
  variant = 'primary',
  size = '',
  className = '',
  icon = null,
  block = false,
}) => {
  const classes = `btn btn-${variant} ${size ? `btn-${size}` : ''} ${block ? 'w-100' : ''} ${className}`;

  // If it's a link (internal)
  if (to) {
    return (
      <Link to={to} className={classes} onClick={onClick}>
        {icon && <i className={`${icon} me-2`}></i>}
        {children}
      </Link>
    );
  }

  // If it's an external link
  if (href) {
    return (
      <a href={href} className={classes} onClick={onClick}>
        {icon && <i className={`${icon} me-2`}></i>}
        {children}
      </a>
    );
  }

  // Regular button
  return (
    <button type={type} className={classes} onClick={onClick}>
      {icon && <i className={`${icon} me-2`}></i>}
      {children}
    </button>
  );
};

Button.propTypes = {
  children: PropTypes.node.isRequired,
  to: PropTypes.string,
  href: PropTypes.string,
  onClick: PropTypes.func,
  type: PropTypes.string,
  variant: PropTypes.string,
  size: PropTypes.string,
  className: PropTypes.string,
  icon: PropTypes.string,
  block: PropTypes.bool,
};

export default Button;

