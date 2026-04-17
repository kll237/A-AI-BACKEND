"use client";

import * as React from "react";

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, ...props }, ref) => {
    // 确保值在0-100之间
    const clampedValue = Math.min(100, Math.max(0, value));
    
    return (
      <div
        ref={ref}
        className={`relative h-4 w-full overflow-hidden rounded-full bg-gray-200 ${className || ""}`}
        {...props}
      >
        <div
          className="h-full w-full flex-1 bg-blue-500 transition-all"
          style={{ 
            width: `${clampedValue}%`,
            transition: "width 0.3s ease-in-out"
          }}
        />
      </div>
    );
  }
);

Progress.displayName = "Progress";

export { Progress };
