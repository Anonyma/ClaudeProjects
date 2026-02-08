import React from 'react';

interface StepCardProps {
  number: string;
  title: string;
  description: string;
  iconUrl: string;
  variant?: 'home' | 'donors';
}

const StepCard: React.FC<StepCardProps> = ({
  number,
  title,
  description,
  iconUrl,
  variant = 'home',
}) => {
  if (variant === 'donors') {
    return (
      <div className="relative w-[293px] h-[303px]">
        <div className="absolute inset-0 bg-white rounded-card shadow-card" />
        <div className="relative px-[26px] py-[33px]">
          <p className="font-karla font-normal text-[24.5px] leading-[1.39] text-black">
            {description}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-[237px]">
      {/* Number */}
      <p className="font-montserrat font-bold text-[42px] leading-none text-black mb-[28px]">
        {number}
      </p>

      {/* Title */}
      <h3 className="font-montserrat font-bold text-[22px] leading-[1.24] text-black mb-[24px] max-w-[188px]">
        {title}
      </h3>

      {/* Card Background */}
      <div className="relative w-full h-[345px] rounded-card overflow-hidden mb-[28px]">
        <div className="absolute inset-0 opacity-70">
          <img
            src="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            alt=""
            className="w-full h-full object-cover"
          />
        </div>

        {/* Icon */}
        <div className="absolute bottom-[16px] left-1/2 -translate-x-1/2">
          <img
            src={iconUrl}
            alt=""
            className="w-auto max-h-[128px] drop-shadow-step"
          />
        </div>
      </div>

      {/* Description */}
      <p className="font-karla font-normal text-[18px] leading-[1.22] text-black max-w-[200px]">
        {description}
      </p>
    </div>
  );
};

export default StepCard;
