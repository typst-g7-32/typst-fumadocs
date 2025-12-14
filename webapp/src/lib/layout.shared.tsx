import { BookIcon } from 'lucide-react';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

export function baseOptions(): BaseLayoutProps {
  return {
    nav: {
      title: 'Typst Fumadocs',
    },
    links: [
      {
        icon: <BookIcon />,
        text: 'Original Docs',
        url: 'https://typst.app/docs/',
        secondary: false,
      },
    ],
    githubUrl: 'https://github.com/typst-g7-32/typst-fumadocs',
  };
}
