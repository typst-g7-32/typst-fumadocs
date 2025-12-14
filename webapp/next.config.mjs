import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  reactStrictMode: true,
  webpack: (config, { isServer }) => {
    config.module.rules.push({
      test: /\.svg$/,
      use: ["@svgr/webpack"],
    });
    if (isServer) {
      config.externals.push({
        canvas: 'canvas',
        "@myriaddreamin/typst-ts-node-compiler": "@myriaddreamin/typst-ts-node-compiler",
      });
    }
  },
};

export default withMDX(config);
