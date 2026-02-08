import { cn } from "@/lib/utils";

interface SectionProps {
  children: React.ReactNode;
  className?: string;
  id?: string;
}

export function Section({ children, className, id }: SectionProps) {
  return (
    <section id={id} className={cn("max-w-[1440px] mx-auto px-[60px] relative w-full", className)}>
      {children}
    </section>
  );
}
