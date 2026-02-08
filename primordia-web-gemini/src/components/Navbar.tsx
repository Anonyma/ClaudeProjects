import Link from "next/link";
import { Button } from "./Button";

export function Navbar() {
  return (
    <nav className="h-[100px] flex items-center justify-between px-[60px] max-w-[1440px] mx-auto w-full bg-white relative z-50">
      {/* Logo */}
      <Link href="/" className="font-futura font-bold text-26 tracking-[-1.82px] leading-none">
        PRIMORDIA
      </Link>

      {/* Links */}
      <div className="flex items-center">
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity w-[126px] text-center">
          About
        </Link>
        <div className="w-[61px] flex justify-center">
             <img src="/images/line.png" alt="" className="h-[61px] w-[1px]" />
        </div>
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity w-[148px] text-center">
          How it Works
        </Link>
        <div className="w-[61px] flex justify-center">
             <img src="/images/line.png" alt="" className="h-[61px] w-[1px]" />
        </div>
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity w-[109px] text-center">
          Lab Notes
        </Link>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" className="w-[172px]">
          For Donors
        </Button>
        <Button variant="outline" size="sm" className="w-[207px]">
          For Applicants
        </Button>
      </div>
    </nav>
  );
}