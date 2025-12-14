declare module '@myriaddreamin/typst.ts/dist/esm/contrib/all-in-one-lite.bundle.js' {
  const lib: any;
  export default lib;
}

interface TypstCompilerOptions {
  getModule: () => string;
}

interface TypstRendererOptions {
  getModule: () => string;
}

interface TypstSvgOptions {
  mainContent: string;
}

interface TypstModule {
  setCompilerInitOptions(options: TypstCompilerOptions): void;
  setRendererInitOptions(options: TypstRendererOptions): void;
  svg(options: TypstSvgOptions): Promise<string>;
}

interface Window {
  $typst?: TypstModule;
}
