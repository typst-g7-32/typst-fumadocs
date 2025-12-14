"use client"

import Image from "next/image"
import { twMerge } from "tailwind-merge"

interface TypstOutputProps {
  imagePath: string | null
  alt?: string
  layout?: "horizontal" | "vertical"
}

export function TypstOutput({
  imagePath,
  alt = "Typst rendered output",
  layout = "horizontal",
}: TypstOutputProps) {
  
  const outputBlockClass = twMerge(
    "flex items-center justify-center p-4 shadow-sm bg-fd-card rounded-lg relative overflow-hidden",
    layout === "horizontal" ? "w-1/2" : "w-full"
  )

  if (!imagePath) {
    return (
      <div className={outputBlockClass}>
        <div className="text-fd-muted-foreground text-sm text-center">
          No output image
        </div>
      </div>
    )
  }

  return (
    <div className={outputBlockClass}>
      <Image
        src={imagePath}
        alt={alt}
        width={800}
        height={600}
        className="w-full h-auto object-contain mt-0 mb-0"
        unoptimized
      />
    </div>
  )
}
