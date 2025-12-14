import defaultMdxComponents from 'fumadocs-ui/mdx';
import type { MDXComponents } from 'mdx/types';

import { TypstPreview } from '@/components/typst/preview';

export const customComponents = {
  TypstPreview,
};

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...components,
    ...customComponents,
  };
}
