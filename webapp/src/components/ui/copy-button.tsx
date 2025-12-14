'use client';

import { type ComponentProps, type RefObject } from 'react';
import { buttonVariants } from '@/components/fumadocs/button';
import { Check, Clipboard } from 'lucide-react'
import { twMerge } from 'tailwind-merge';

import { useCopyButton } from 'fumadocs-ui/utils/use-copy-button';

export function CopyButton({
  className,
  containerRef,
  ...props
}: ComponentProps<'button'> & {
  containerRef: RefObject<HTMLElement | null>;
}) {
  const [checked, onClick] = useCopyButton(() => {
    const pre = containerRef.current?.getElementsByTagName('pre').item(0);
    if (!pre) return;


    const clone = pre.cloneNode(true) as HTMLElement;
    clone.querySelectorAll('.nd-copy-ignore').forEach((node) => {
      node.replaceWith('\n');
    });


    void navigator.clipboard.writeText(clone.textContent ?? '');
  });


  return (
    <button
      type="button"
      data-checked={checked || undefined}
      className={twMerge(
        buttonVariants({
          className:
            'hover:text-fd-accent-foreground data-checked:text-fd-accent-foreground',
          size: 'icon-xs',
        }),
        className,
      )}
      aria-label={checked ? 'Copied Text' : 'Copy Text'}
      onClick={onClick}
      {...props}
    >
      {checked ? <Check /> : <Clipboard />}
    </button>
  );
}