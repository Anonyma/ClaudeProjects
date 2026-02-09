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
    <div className="relative w-[230px] flex flex-col">
      {/* Number */}
      <p className="font-montserrat font-bold text-[42px] leading-none text-black mb-[8px]">
        {number}
      </p>

      {/* Title */}
      <h3 className="font-montserrat font-bold text-[20px] leading-[1.2] text-black mb-[16px] min-h-[50px]">
        {title}
      </h3>

      {/* Icon - positioned HALF IN / HALF OUT of card (50% overlap) */}
      <div className="relative w-full flex justify-center mb-[-50px] z-10">
        <img
          src={iconUrl}
          alt=""
          className="w-auto h-[100px] object-contain drop-shadow-step"
        />
      </div>

      {/* Card Background with text INSIDE */}
      <div className="relative w-full h-[270px] rounded-card overflow-hidden">
        <div className="absolute inset-0 opacity-70">
          <img
            src="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
            alt=""
            className="w-full h-full object-cover"
          />
        </div>

        {/* Description - INSIDE green box */}
        <div className="relative h-full flex items-end pb-[20px] px-[16px]">
          <p className="font-karla font-normal text-[17px] leading-[1.24] text-black">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
};

export default StepCard;
