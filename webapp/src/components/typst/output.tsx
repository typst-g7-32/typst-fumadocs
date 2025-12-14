"use client"

import Image from "next/image"
import { useState, useEffect } from "react"
import { LoadingSpinner } from "@/components/ui/spinner"
import { twMerge } from "tailwind-merge"
import { AlertTriangle, X } from "lucide-react"
import { buttonVariants } from "../fumadocs/button"

interface TypstOutputProps {
  compiledSvg: string | null
  imagePath: string | null
  alt: string
  compileError: string | null
  imageError: boolean
  onImageError: () => void
  layout?: "horizontal" | "vertical"
}

export function TypstOutput({
  compiledSvg,
  imagePath,
  alt,
  compileError,
  imageError,
  onImageError,
  layout = "horizontal",
}: TypstOutputProps) {
  const [imageLoading, setImageLoading] = useState(true)
  const [svgLoading, setSvgLoading] = useState(true)
  const [showErrorDetails, setShowErrorDetails] = useState(false)

  useEffect(() => {
    if (compiledSvg) {
      const timer = setTimeout(() => {
        setSvgLoading(false)
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [compiledSvg])

  useEffect(() => {
    if (imagePath) {
      const timer = setTimeout(() => {
        setImageLoading(false)
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [imagePath])

  const outputBlockClass =
    layout === "horizontal"
      ? "w-1/2 flex items-center justify-center p-4 bg-fd-card rounded-lg relative overflow-hidden"
      : "w-full flex items-center justify-center p-4 bg-fd-card rounded-lg relative overflow-hidden"

  const showSpinner = (compiledSvg && svgLoading) || (imagePath && !imageError && imageLoading)
  const showNoOutput = !compiledSvg && (!imagePath || imageError)

  return (
    <div className={outputBlockClass}>
      {showSpinner && (
        <div className="absolute inset-0 flex items-center justify-center bg-fd-card backdrop-blur-sm z-10">
          <LoadingSpinner />
        </div>
      )}

      {compiledSvg ? (
        <div
          className={twMerge(
            "w-full h-full flex items-center justify-center transition-opacity duration-200",
            svgLoading ? "opacity-0" : "opacity-100"
          )}
          style={{ maxWidth: '800px', maxHeight: '600px' }}
          dangerouslySetInnerHTML={{ __html: compiledSvg }}
        />
      ) : imagePath && !imageError ? (
        <Image
          src={imagePath}
          alt={alt}
          width={800}
          height={600}
          className={twMerge(
            "w-full h-auto object mt-0 mb-0 transition-opacity duration-200",
            imageLoading ? "opacity-0" : "opacity-100"
          )}
          onError={() => {
            onImageError()
            setImageLoading(false)
          }}
          onLoad={() => setImageLoading(false)}
          unoptimized
        />
      ) : showNoOutput ? (
        <div className="text-fd-muted-foreground text-sm text-center p-4">
          <div>No output</div>
          {imagePath && (
            <div className="text-xs mt-2 opacity-70 break-all font-mono">
              {imagePath}
            </div>
          )}
        </div>
      ) : null}

      {compileError && (
        <>
          {showErrorDetails ? (
            <div className="absolute top-2 left-2 right-2 p-3 bg-fd-card backdrop-blur-md border rounded-md shadow-lg z-20 animate-in fade-in zoom-in-95 duration-200">
              <div className="flex items-start justify-between mb-1">
                <div className="text-fd-foreground text-sm font-medium">
                  Compilation error
                </div>
                <button 
                  onClick={() => setShowErrorDetails(false)}
                  className="text-fd-muted-foreground transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="text-xs font-mono break-all max-h-37.5 overflow-auto">
                {compileError}
              </div>
            </div>
          ) : (
            
            <button
              onClick={() => setShowErrorDetails(true)}
              className={twMerge(buttonVariants({
                className: "absolute top-2 right-2 z-2 backdrop-blur-lg bg-fd-card rounded-lg text-fd-muted-foreground",
                size: "icon-xs",
              }))}
              title="View Error"
            >
              <AlertTriangle className="w-5 h-5" />
            </button>
          )}
        </>
      )}
    </div>
  )
}
