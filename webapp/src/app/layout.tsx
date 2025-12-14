import type { Metadata } from 'next';
import { RootProvider } from 'fumadocs-ui/provider/next';
import './global.css';
import { Inter } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
});


export const metadata: Metadata = {
  title: 'Typst Fumadocs',
  description: 'Fumadocs Typst documentation',
  metadataBase: new URL('https://typst-g7-32.github.io/typst-fumadocs/ '), 
};

export default function Layout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex flex-col min-h-screen">
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}
