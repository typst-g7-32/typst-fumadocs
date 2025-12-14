export const TYPST_CONFIG = {
  version: '0.7.0-rc1',
  cdn: 'https://cdn.jsdelivr.net/npm',
} as const;

export const getTypstCompilerUrl = () =>
  `${TYPST_CONFIG.cdn}/@myriaddreamin/typst-ts-web-compiler@${TYPST_CONFIG.version}/pkg/typst_ts_web_compiler_bg.wasm`;

export const getTypstRendererUrl = () =>
  `${TYPST_CONFIG.cdn}/@myriaddreamin/typst-ts-renderer@${TYPST_CONFIG.version}/pkg/typst_ts_renderer_bg.wasm`;
