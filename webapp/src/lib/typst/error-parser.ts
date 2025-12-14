import { ParsedTypstError, DiagMessage } from "../types/compiler-error"

export function parseTypstError(error: unknown): ParsedTypstError {
  const errorStr = typeof error === 'string' 
    ? error 
    : error instanceof Error 
      ? error.message 
      : String(error)

  const diagnostics: DiagMessage[] = []
  
  const matches = errorStr.matchAll(/SourceDiagnostic\s*\{\s*severity:\s*(\w+),\s*span:\s*Span\([^)]+\),\s*message:\s*"([^"]+)",\s*trace:\s*\[[^\]]*\],\s*hints:\s*\[([^\]]*)\]\s*\}/g)
  
  for (const match of matches) {
    const severity = match[1].toLowerCase() === 'warning' ? 'warning' : 'error'
    const message = match[2]
    const hintsStr = match[3].trim()
    
    const hints: string[] = hintsStr
      ? hintsStr.split(',').map(h => h.trim().replace(/^"(.*)"$/, '$1')).filter(h => h.length > 0)
      : []

    diagnostics.push({ message, severity, hints })
  }

  return { diagnostics }
}

export function formatTypstError(parsed: ParsedTypstError): string {
  return parsed.diagnostics
    .map(d => {
      const message = d.message.charAt(0).toUpperCase() + d.message.slice(1)
      const hints = d.hints.length > 0 ? `\nHints: ${d.hints.join(', ')}` : ''
      return `${message}${hints}`
    })
    .join('\n\n')
}