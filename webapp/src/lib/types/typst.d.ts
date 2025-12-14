declare module "@myriaddreamin/typst.ts/dist/esm/contrib/all-in-one-lite.bundle.js" {
  interface TypstModule {
    setCompilerInitOptions(options: {
      getModule: () => string
    }): void
    setRendererInitOptions(options: {
      getModule: () => string
    }): void
    svg(options: { mainContent: string }): Promise<string>
    render(options: { mainContent: string }): Promise<unknown>
  }

  const typst: TypstModule
  export default typst
}

declare global {
  interface Window {
    $typst: TypstModule | undefined
  }
}
