import React from 'react';
import Link from 'next/link';
import Button from './Button';
import Image from 'next/image';

const MenuBar: React.FC = () => {
  return (
    <nav className="absolute top-0 left-0 w-full h-[100px] z-50">
      <div className="relative h-full max-w-[1440px] mx-auto px-[72px]">
        {/* Logo */}
        <Link
          href="/"
          className="absolute left-[72px] top-[44px] font-futura font-bold text-[26px] tracking-[-1.82px] text-black"
        >
          PRIMORDIA
        </Link>

        {/* Menu Items */}
        <div className="absolute left-[294px] top-[44px] flex items-center gap-[54px]">
          <Link
            href="#about"
            className="font-karla font-semibold text-[23px] text-black hover:opacity-70 transition-opacity"
          >
            About
          </Link>
          <div className="w-px h-[61px] -rotate-90 opacity-0">
            <Image
              src="http://localhost:3845/assets/6e151bd92ad5e84b4d1076b969e8ea9697131126.svg"
              alt=""
              width={1}
              height={61}
            />
          </div>

          <Link
            href="#how-it-works"
            className="font-karla font-semibold text-[23px] text-black hover:opacity-70 transition-opacity"
          >
            How it Works
          </Link>
          <div className="w-px h-[61px] -rotate-90 opacity-0">
            <Image
              src="http://localhost:3845/assets/6e151bd92ad5e84b4d1076b969e8ea9697131126.svg"
              alt=""
              width={1}
              height={61}
            />
          </div>

          <Link
            href="#lab-notes"
            className="font-karla font-semibold text-[23px] text-black hover:opacity-70 transition-opacity"
          >
            Lab Notes
          </Link>
        </div>

        {/* Action Buttons */}
        <div className="absolute right-[72px] top-[34px] flex items-center gap-[21px]">
          <Button variant="nav" size="sm" href="/fund">
            For Donors
          </Button>
          <Button variant="nav" size="sm" href="/apply">
            For Applicants
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default MenuBar;
