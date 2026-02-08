import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "outline";
  size?: "default" | "sm";
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "rounded-39 font-karla font-medium flex items-center justify-center transition-colors disabled:opacity-50 disabled:cursor-not-allowed border-[2.5px] border-black",
          {
            "bg-black text-white hover:bg-white hover:text-black": variant === "primary",
            "bg-transparent text-black hover:bg-black hover:text-white": variant === "outline",
            "h-[56px] text-28 px-8": size === "default",
            "h-[40px] text-20 px-6": size === "sm",
          },
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button };
