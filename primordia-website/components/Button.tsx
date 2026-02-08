import React from 'react';
import Link from 'next/link';

type ButtonVariant = 'primary' | 'secondary' | 'nav' | 'status';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  href?: string;
  onClick?: () => void;
  className?: string;
  fixedWidth?: string;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  href,
  onClick,
  className = '',
  fixedWidth,
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-karla font-medium border-[2.5px] transition-colors leading-none';

  const variantStyles = {
    primary: 'bg-black border-black text-white hover:bg-gray-800',
    secondary: 'bg-white border-black text-black hover:bg-gray-50',
    nav: 'bg-transparent border-black text-black hover:bg-gray-50',
    status: 'bg-white border-black text-black text-[23px] h-[42px] px-6',
  };

  const sizeStyles = {
    sm: 'h-[40px] px-6 text-[20px] rounded-button',
    md: 'h-[56px] px-8 text-[28px] rounded-button',
    lg: 'h-[56px] px-10 text-[29px] rounded-button',
  };

  const widthStyle = fixedWidth ? { width: fixedWidth } : {};
  const classes = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

  if (href) {
    return (
      <Link href={href} className={classes} style={widthStyle}>
        {children}
      </Link>
    );
  }

  return (
    <button onClick={onClick} className={classes} style={widthStyle}>
      {children}
    </button>
  );
};

export default Button;
