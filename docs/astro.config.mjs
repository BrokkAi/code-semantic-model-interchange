import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

const site = process.env.PUBLIC_DOCS_SITE ?? 'https://csmi.brokk.ai';
const productionBase = process.env.PUBLIC_DOCS_BASE ?? '/';
const isDev = process.argv.includes('dev');
const socialPreview = new URL('/og.png', site).href;

export default defineConfig({
  site,
  base: isDev ? '/' : productionBase,
  integrations: [
    starlight({
      title: 'CSMI',
      description: 'Code Semantic Model Interchange — an experimental, analyzer-neutral semantic model interchange specification.',
      customCss: ['./src/styles/csmi.css'],
      favicon: '/favicon.svg',
      head: [
        { tag: 'meta', attrs: { property: 'og:image', content: socialPreview } },
        { tag: 'meta', attrs: { property: 'og:image:width', content: '1200' } },
        { tag: 'meta', attrs: { property: 'og:image:height', content: '630' } },
        {
          tag: 'meta',
          attrs: {
            property: 'og:image:alt',
            content: 'Code Semantic Model Interchange — portable semantic knowledge for independent code-analysis tools.',
          },
        },
        { tag: 'meta', attrs: { name: 'twitter:image', content: socialPreview } },
        {
          tag: 'meta',
          attrs: {
            name: 'twitter:image:alt',
            content: 'Code Semantic Model Interchange — portable semantic knowledge for independent code-analysis tools.',
          },
        },
      ],
      components: {
        Footer: './src/components/Footer.astro',
      },
      editLink: {
        baseUrl: 'https://github.com/BrokkAi/code-semantic-model-interchange/edit/main/docs/',
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/BrokkAi/code-semantic-model-interchange',
        },
      ],
      sidebar: [
        {
          label: 'Start',
          items: [
            { label: 'Overview', slug: 'overview' },
            { label: 'Status and versioning', slug: 'status' },
          ],
        },
        {
          label: 'Specification · v0.1',
          items: [
            { label: 'Specification architecture', slug: 'specification/architecture' },
            { label: 'Full v0.1 specification', slug: 'specification/v0-1' },
            { label: 'Python profile 0.1', slug: 'profiles/python' },
            { label: 'JavaScript, TypeScript, and Node', slug: 'profiles/javascript-typescript-node' },
            { label: 'Java/JVM profiles', slug: 'profiles/jvm' },
            { label: 'Rust profile 0.1', slug: 'profiles/rust' },
            { label: 'Value-transfer profile 0.1', slug: 'profiles/value-transfer' },
            { label: 'C and C++ profile 0.1', slug: 'profiles/cpp' },
          ],
        },
        {
          label: 'Implement',
          items: [
            { label: 'JSON Schema', slug: 'implement/schema' },
            { label: 'Examples and fixtures', slug: 'implement/examples' },
          ],
        },
      ],
    }),
  ],
});
