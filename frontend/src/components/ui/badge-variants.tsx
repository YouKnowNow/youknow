import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-sm font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        secondary: "bg-secondary text-secondary-foreground",
        destructive: "bg-destructive text-destructive-foreground",
        outline: "border border-border text-foreground",
        focus: "bg-focus text-focus-foreground",
        success: "bg-success text-success-foreground",
        warning: "bg-warning text-warning-foreground",
        interest: "bg-gradient-to-r from-primary to-chart-quaternary text-primary-foreground",
      },
      size: {
        default: "px-3 py-1 text-sm",
        sm: "px-2 py-0.5 text-xs",
        lg: "px-4 py-2 text-base",
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}

export { Badge, badgeVariants };