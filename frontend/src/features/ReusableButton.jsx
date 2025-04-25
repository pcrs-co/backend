import React from 'react';
import PropTypes from 'prop-types';
import { Link, useNavigate } from 'react-router-dom';
import { ACCESS_TOKEN } from '../utils/constants';

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
  logout = false,
}) => {
  const navigate = useNavigate();
  const classes = `btn btn-${variant} ${size ? `btn-${size}` : ''} ${block ? 'w-100' : ''} ${className}`;

  const handleClick = (e) => {
    if (logout) {
      e.preventDefault(); // prevent default link or form behavior
      localStorage.removeItem(ACCESS_TOKEN);
      navigate('/login'); // or navigate('/')
    }

    if (onClick) {
      onClick(e);
    }
  };

  if (to) {
    return (
      <Link to={to} className={classes} onClick={handleClick}>
        {icon && <i className={`${icon} me-2`}></i>}
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a href={href} className={classes} onClick={handleClick}>
        {icon && <i className={`${icon} me-2`}></i>}
        {children}
      </a>
    );
  }

  return (
    <button type={type} className={classes} onClick={handleClick}>
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
  logout: PropTypes.bool,
};

export default Button;
