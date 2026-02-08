import React from 'react';
import Link from 'next/link';

const Footer: React.FC = () => {
  return (
    <footer className="relative w-full h-[236px] overflow-hidden">
      {/* Background gradient image */}
      <div className="absolute inset-0">
        <img
          src="http://localhost:3845/assets/b19a591256bc5de634d2547a52cfb3c58c3b47d0.png"
          alt=""
          className="w-full h-full object-cover opacity-70"
        />
      </div>

      <div className="relative h-full max-w-[1440px] mx-auto px-[120px] py-[40px]">
        <div className="flex justify-between items-start h-full">
          {/* Left Column - Navigation Links */}
          <div className="font-karla font-semibold text-[26px] leading-[1.88] text-black space-y-1">
            <Link href="/apply" className="block hover:opacity-70 transition-opacity">
              For Experiments
            </Link>
            <Link href="/fund" className="block hover:opacity-70 transition-opacity">
              For Donors
            </Link>
            <Link href="/privacy" className="block hover:opacity-70 transition-opacity">
              Privacy Policy
            </Link>
          </div>

          {/* Right Column - Attribution */}
          <div className="text-right">
            <p className="font-karla font-medium text-[22px] leading-[1.3] text-black max-w-[446px]">
              Primordia Grants is a cross collaboration between ValleyDAO & Biopunk Labs
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
