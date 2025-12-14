"use client"

import { useEffect, useRef, useLayoutEffect, useState } from "react"
import { EditorView, keymap } from '@codemirror/view'
import { EditorState, Compartment } from '@codemirror/state'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import shiki from 'codemirror-shiki'
import { createHighlighterCore } from 'shiki/core'
import { createOnigurumaEngine } from 'shiki/engine/oniguruma'
import { twMerge } from 'tailwind-merge';

import { wrappedLineIndent } from 'codemirror-wrapped-line-indent'
import { LoadingSpinner } from '@/components/ui/spinner'
import { CopyButton } from "../ui/copy-button"

interface TypstEditorProps {
  code: string
  onChange: (code: string) => void
  wordWrap?: boolean
  title?: string
  icon?: React.ReactNode
  allowCopy?: boolean
  className?: string
  onLoadingChange?: (isLoading: boolean) => void
}

const highlighterPromise = createHighlighterCore({
  langs: [
    import('@shikijs/langs/typst'),
    import('@shikijs/langs/javascript'),
  ],
  themes: [
    import('@shikijs/themes/github-dark'),
  ],
  engine: createOnigurumaEngine(import('shiki/wasm')),
})

export function TypstEditor({
  code,
  onChange,
  wordWrap = true,
  title,
  icon,
  allowCopy = true,
  className,
  onLoadingChange,
}: TypstEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null)
  const viewRef = useRef<EditorView | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)

  const shikiCompartment = useRef(new Compartment())

  const onChangeRef = useRef(onChange)
  useLayoutEffect(() => {
    onChangeRef.current = onChange
  }, [onChange])

  useEffect(() => {
    if (!editorRef.current) return
    let mounted = true

    const init = async () => {
      if (!mounted) return

      setIsLoading(true)
      onLoadingChange?.(true)

      try {
        const themeId = 'github-dark'

        const state = EditorState.create({
          doc: code ?? '',
          extensions: [
            history(),
            keymap.of(historyKeymap),
            keymap.of(defaultKeymap),
            keymap.of([indentWithTab]),
            wordWrap ? [EditorView.lineWrapping] : [],
            wordWrap ? wrappedLineIndent : [],

            EditorView.updateListener.of((update) => {
              if (update.docChanged) {
                const value = update.state.doc.toString()
                onChangeRef.current(value)
              }
            }),
            EditorView.darkTheme.of(true),
            shiki({
              highlighter: highlighterPromise,
              language: 'typst',
              theme: themeId,
            }),
            shikiCompartment.current.of([]),
          ],
        })

        if (mounted && editorRef.current && !viewRef.current) {
          viewRef.current = new EditorView({
            state,
            parent: editorRef.current,
          })
        }

        setIsLoading(false)
        onLoadingChange?.(false)
      } catch (error) {
        console.error('Failed to initialize editor:', error)
        setIsLoading(false)
        onLoadingChange?.(false)
      }
    }

    init()

    return () => {
      mounted = false
      if (viewRef.current) {
        viewRef.current.destroy()
        viewRef.current = null
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <figure
      ref={containerRef}
      dir="ltr"
      className={twMerge(
        'my-4 bg-fd-card rounded-xl',
        'shiki relative border shadow-sm outline-none text-sm mt-0 mb-0',
        className,
      )}
    >
      {title ? (
        <div className="flex text-fd-muted-foreground items-center gap-2 h-9.5 border-b px-4">
          {typeof icon === 'string' ? (
            <div
              className="[&_svg]:size-3.5"
              dangerouslySetInnerHTML={{
                __html: icon,
              }}
            />
          ) : (
            icon
          )}
          <figcaption className="flex-1 truncate">{title}</figcaption>
          {allowCopy && (
            <CopyButton containerRef={containerRef} className="-me-2" />
          )}
        </div>
      ) : (
        allowCopy && (
          <div className="absolute top-2 right-2 z-2 backdrop-blur-lg rounded-lg text-fd-muted-foreground">
            <CopyButton containerRef={containerRef} />
          </div>
        )
      )}
      <div
        className={twMerge(
          'text-[13px] py-3.5 px-2 overflow-auto max-h-150 fd-scroll-container relative',
          !title && 'pr-8',
        )}
        style={
          {
            '--padding-right': !title ? 'calc(var(--spacing) * 8)' : undefined,
          } as object
        }
      >
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-fd-card/80 backdrop-blur-sm z-10">
            <LoadingSpinner />
          </div>
        )}
        <div
          ref={editorRef}
          className="font-mono"
          style={{ fontSize: "14px" }}
        />
      </div>
    </figure>
  )
}
