"use client"

import { useState, useMemo, useCallback, useEffect, ReactNode, isValidElement } from "react"
import { useTypstCompiler } from "@/hooks/use-typst-compiler"
import stripIndent from 'strip-indent';

import { TypstEditor } from "./editor"
import { TypstOutput } from "./output"
import { DynamicCodeBlock } from "@/components/fumadocs/dynamic-codeblock"
import { formatTypstError, parseTypstError } from "@/lib/typst/error-parser"
import { DEFAULT_HIDDEN_PREFIX, DEFAULT_HIDDEN_SUFFIX } from "@/lib/typst/constants"
import { LoadingSpinner } from "@/components/ui/spinner"

interface TypstPreviewProps {
  code: string
  image: string
  alt?: string
  layout?: "horizontal" | "vertical"
  wordWrap?: boolean
  editable?: boolean
  hiddenPrefix?: string | null
  hiddenSuffix?: string | null
}

function buildFullCode(
  code: string,
  hiddenPrefix: string | null | undefined,
  hiddenSuffix: string | null | undefined
): string {
  const prefix = hiddenPrefix || ""
  const suffix = hiddenSuffix || ""
  return `${prefix}${code}${suffix}`
}

export function TypstPreview({
  code,
  image,
  alt = "Preview",
  layout = "horizontal",
  wordWrap = true,
  editable = true,
  hiddenPrefix = DEFAULT_HIDDEN_PREFIX,
  hiddenSuffix = DEFAULT_HIDDEN_SUFFIX,
}: TypstPreviewProps) {
  const [imageError, setImageError] = useState(false)
  const [compiledSvg, setCompiledSvg] = useState<string | null>(null)
  const [localCompileError, setLocalCompileError] = useState<string | null>(null)
  const [initialCompileDone, setInitialCompileDone] = useState(false)

  const {
    compile,
    isLoading: compilerLoading,
    compilerInitError,
    compileError: hookCompileError
  } = useTypstCompiler()

  const displayCode = useMemo(() => {
    return stripIndent(code.trim());
  }, [code])

  const imagePath = useMemo(() => {
    if (image.startsWith("/")) {
      return image
    }
    return `/assets/${image}`
  }, [image])

  const isEditable = editable && !compilerLoading && !compilerInitError && !!compile

  const compileCode = useCallback(
    async (codeToCompile: string) => {
      if (!compile) {
        return
      }

      setLocalCompileError(null)

      try {
        const fullCodeToCompile = buildFullCode(codeToCompile, hiddenPrefix, hiddenSuffix)

        const svg = await compile(fullCodeToCompile)

        if (!svg) {
          throw new Error("Compiler returned empty result")
        }

        if (typeof svg !== "string") {
          throw new Error("Compiler returned invalid type of SVG")
        }

        const trimmedSvg = svg.trim()
        if (!trimmedSvg.startsWith("<svg")) {
          throw new Error("Invalid svg: does not start with <svg")
        }

        const processed = trimmedSvg
          .replace(/width="[^"]*"/g, '')
          .replace(/height="[^"]*"/g, '')

        setCompiledSvg(processed)
        setLocalCompileError(null)
      } catch (error: unknown) {
        const parsedError = parseTypstError(error)
        const message = formatTypstError(parsedError)
        setLocalCompileError(message)
        console.log("Compilation error:", error)
      } finally {
        setInitialCompileDone(true)
      }
    },
    [compile, hiddenPrefix, hiddenSuffix]
  )

  useEffect(() => {
    if (isEditable && typeof compile === 'function' && !initialCompileDone) {
      compileCode(displayCode)
    }
  }, [isEditable, compile, displayCode, compileCode, initialCompileDone])

  const handleEditorChange = useCallback(
    (newCode: string) => {
      compileCode(newCode)
    },
    [compileCode]
  )

  const containerClass =
    layout === "horizontal"
      ? "flex flex-row gap-8 items-stretch"
      : "flex flex-col gap-8"

  const codeBlockClass = layout === "horizontal" ? "w-1/2" : "w-full"

  const displayCompileError = localCompileError || hookCompileError

  const showCompilerLoading = editable && compilerLoading

  return (
    <div className="typst-render-container my-6">
      {showCompilerLoading ? (
        <div className="flex items-center justify-center p-12 bg-fd-card border rounded-lg">
          <LoadingSpinner />
          <span className="ml-3 text-fd-muted-foreground">Loading compiler...</span>
        </div>
      ) : (
        <div className={containerClass}>
          <div className={`${codeBlockClass}`}>
            {isEditable ? (
              <TypstEditor
                code={displayCode}
                onChange={handleEditorChange}
                wordWrap={wordWrap}
              />
            ) : (
              <DynamicCodeBlock
                code={displayCode}
                lang="typst"
                wordWrap={wordWrap}
                codeblock={{
                  className: "h-full"
                }}
              />
            )}
          </div>

          <TypstOutput
            compiledSvg={compiledSvg}
            imagePath={imagePath}
            alt={alt}
            compileError={displayCompileError}
            imageError={imageError}
            onImageError={() => setImageError(true)}
            layout={layout}
          />
        </div>
      )}
    </div>
  )
}
