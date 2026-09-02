import { copyFile, mkdir, readdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, '../..');
const sourcePath = resolve(repositoryRoot, 'spec/0.1/specification.md');
const schemaSourcePath = resolve(repositoryRoot, 'spec/0.1/schema.json');
const outputPath = resolve(
  repositoryRoot,
  'docs/src/content/docs/specification/v0-1.md',
);
const schemaOutputPath = resolve(
  repositoryRoot,
  'docs/public/schema/0.1/schema.json',
);
const repositoryRevision = /^[0-9a-f]{40}$/i.test(process.env.GITHUB_SHA ?? '')
  ? process.env.GITHUB_SHA
  : 'main';
const revisionLabel = repositoryRevision === 'main'
  ? repositoryRevision
  : repositoryRevision.slice(0, 12);
const sourceRevisionUrl = `https://github.com/BrokkAi/code-semantic-model-interchange/tree/${repositoryRevision}`;

const source = await readFile(sourcePath, 'utf8');
const body = source.replace(/^# Code Semantic Model Interchange v0\.1\n+/, '');
const headings = [...source.matchAll(/^(#{2,3})\s+(.+)$/gm)].map((match) => ({
  depth: match[1].length,
  title: match[2].trim(),
}));

function slugifyHeading(title) {
  return title
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}\s-]/gu, '')
    .trim()
    .replace(/\s+/g, '-');
}

function escapeHtml(value) {
  return value
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;');
}

const sections = [];
for (const heading of headings) {
  if (heading.depth === 2) {
    sections.push({ ...heading, children: [] });
  } else {
    sections.at(-1)?.children.push(heading);
  }
}

const tableOfContents = `<nav class="csmi-toc" aria-labelledby="csmi-toc-title">
  <h2 id="csmi-toc-title">Contents</h2>
  <ol>
${sections
  .map(
    (section) => `    <li>
      <a class="csmi-toc__section" href="#${slugifyHeading(section.title)}">${escapeHtml(section.title)}</a>
      <ol>
${section.children
  .map(
    (child) =>
      `        <li><a href="#${slugifyHeading(child.title)}">${escapeHtml(child.title)}</a></li>`,
  )
  .join('\n')}
      </ol>
    </li>`,
  )
  .join('\n')}
  </ol>
</nav>`;

const firstSectionOffset = body.indexOf('## ');
const preamble = body.slice(0, firstSectionOffset).trimEnd();
const sectionBody = body.slice(firstSectionOffset);
const frontmatter = `---
title: Code Semantic Model Interchange v0.1
description: The normative semantic model and conformance specification for CSMI v0.1.
editUrl: https://github.com/BrokkAi/code-semantic-model-interchange/edit/main/spec/0.1/specification.md
---

<span class="csmi-label csmi-label--normative">Normative · generated from repository source</span>

<p class="csmi-revision">
  Published with the <a href="/schema/0.1/schema.json">v0.1 JSON Schema</a> from
  <a href="${sourceRevisionUrl}">source revision <code>${revisionLabel}</code></a>.
</p>

`;

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(
  outputPath,
  `${frontmatter}${preamble}\n\n${tableOfContents}\n\n${sectionBody}`,
  'utf8',
);
await mkdir(dirname(schemaOutputPath), { recursive: true });
await copyFile(schemaSourcePath, schemaOutputPath);

async function publishProfileSchemas(directory, relativeParts = []) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const source = resolve(directory, entry.name);
    const relative = [...relativeParts, entry.name];
    if (entry.isDirectory()) {
      await publishProfileSchemas(source, relative);
    } else if (entry.name === 'schema.json') {
      const destination = resolve(
        repositoryRoot,
        'docs/public/schema/profiles',
        ...relative,
      );
      await mkdir(dirname(destination), { recursive: true });
      await copyFile(source, destination);
    }
  }
}

await publishProfileSchemas(resolve(repositoryRoot, 'profiles'));
