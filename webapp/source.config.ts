import { type RehypeCodeOptions } from 'fumadocs-core/mdx-plugins';
import {
  defineConfig,
  defineDocs,
  frontmatterSchema,
  metaSchema,
} from 'fumadocs-mdx/config';

export const docs = defineDocs({
  dir: 'content/docs',
  docs: {
    schema: frontmatterSchema,
    postprocess: {
      includeProcessedMarkdown: true,
    },
  },
  meta: {
    schema: metaSchema,
  },
});

const rehypeCodeOptions: RehypeCodeOptions = {
  inline: 'tailing-curly-colon',
  themes: {
    light: 'github-light',
    dark: 'github-dark',
  },
};
export default defineConfig({
  mdxOptions: {
    rehypeCodeOptions
  },
});
