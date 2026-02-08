export function Footer() {
  return (
    <footer className="h-[236px] bg-gray-50 flex items-center justify-center relative overflow-hidden">
      {/* Background placeholder - in production would be the image asset */}
      <div className="absolute inset-0 bg-gray-100 opacity-50 z-0" />
      
      <div className="max-w-[1440px] w-full px-[60px] flex justify-between items-center relative z-10 h-full">
        <div className="flex flex-col gap-1 font-karla font-semibold text-26 leading-[1.88]">
          <a href="#" className="hover:underline">For Experiments</a>
          <a href="#" className="hover:underline">For Donors</a>
          <a href="#" className="hover:underline">Privacy Policy</a>
        </div>
        
        <div className="max-w-[446px] text-right font-karla text-20 leading-tight">
             {/* Using text-20 as placeholder for the description text size, verifying visual weight */}
             Primordia Grants is a cross collaboration between ValleyDAO & Biopunk Labs
        </div>
      </div>
    </footer>
  );
}
