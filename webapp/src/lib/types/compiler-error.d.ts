export type DiagSeverity = 'error' | 'warning' | 'hint'

export interface DiagMessage {
  message: string
  severity: DiagSeverity
  hints: string[]
}

export interface ParsedTypstError {
  diagnostics: DiagMessage[]
}