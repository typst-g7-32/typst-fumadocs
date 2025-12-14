"use client"

import { useMemo } from "react"
import { TypstOutput } from "./output"
import { DynamicCodeBlock } from 'fumadocs-ui/components/dynamic-codeblock';

interface TypstPreviewProps {
  code: string
  image: string
  alt?: string
  layout?: "horizontal" | "vertical"
}

export function TypstPreview({
  code,
  image,
  alt = "Typst rendering result",
  layout = "horizontal",
}: TypstPreviewProps) {
  const displayCode = useMemo(() => code.trim(), [code])

  const imagePath = useMemo(() => {
    if (image.startsWith("/")) {
      return image
    }
    return `/docs/attachments/${image}`
  }, [image])

  const containerClass =
    layout === "horizontal"
      ? "flex flex-row gap-8 items-stretch"
      : "flex flex-col gap-8"

  const codeBlockClass = layout === "horizontal" ? "w-1/2" : "w-full"

  return (
    <div className="typst-preview-container my-6">
      <div className={containerClass}>
        <div className={codeBlockClass}>
          <DynamicCodeBlock
            code={displayCode}
            lang="typst"
            codeblock={{
              className: "h-full"
            }}
          />
        </div>

        <TypstOutput
          imagePath={imagePath}
          layout={layout}
          alt={alt}
        />
      </div>
    </div>
  )
}
