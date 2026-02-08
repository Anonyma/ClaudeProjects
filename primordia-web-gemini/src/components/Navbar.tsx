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
      <div className="flex items-center gap-8">
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity">
          About
        </Link>
        {/* Separators in design were complex absolute lines, simplifying to gap for clean React impl */}
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity">
          How it Works
        </Link>
        <Link href="#" className="font-karla font-semibold text-23 leading-none hover:opacity-70 transition-opacity">
          Lab Notes
        </Link>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm">
          For Donors
        </Button>
        <Button variant="outline" size="sm">
          For Applicants
        </Button>
      </div>
    </nav>
  );
}
