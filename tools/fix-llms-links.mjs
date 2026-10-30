// The llms plugin falls back to source paths when Docusaurus does not expose
// routesPaths to postBuild. This site uses frontmatter slugs, so those fallback
// URLs often point to 404s. Rewrite them to the built routes and verify them.
import {existsSync, readFileSync, readdirSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const docs = path.join(root, 'docs');
const build = path.join(root, 'build');
const feed = path.join(build, 'llms.txt');
const base = 'https://libraos.com/docs/';

function* markdownFiles(dir) {
  for (const entry of readdirSync(dir, {withFileTypes: true})) {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) yield* markdownFiles(file);
    else if (/\.mdx?$/.test(entry.name)) yield file;
  }
}

const routes = new Map();
for (const file of markdownFiles(docs)) {
  const source = readFileSync(file, 'utf8');
  const frontmatter = source.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const slug = frontmatter?.[1].match(/^slug:\s*(.+?)\s*$/m)?.[1]
    ?.trim().replace(/^['"]|['"]$/g, '');
  if (!slug) continue;

  const relative = path.relative(docs, file).replace(/\\/g, '/').replace(/\.mdx?$/, '');
  const sourceURL = new URL(relative, base).href;
  const routePath = slug.replace(/^\/+|\/+$/g, '');
  const routeURL = new URL(routePath ? `${routePath}/` : '', base).href;
  routes.set(sourceURL, routeURL);
}

let rewritten = 0;
const content = readFileSync(feed, 'utf8').replace(
  /\]\((https:\/\/libraos\.com\/docs\/[^)]+)\)/g,
  (match, url) => {
    const route = routes.get(url);
    if (!route || route === url) return match;
    rewritten++;
    return `](${route})`;
  },
);

for (const [, url] of content.matchAll(/\]\((https:\/\/libraos\.com\/docs\/[^)]+)\)/g)) {
  const relative = new URL(url).pathname.replace(/^\/docs\/?/, '');
  if (!existsSync(path.join(build, relative, 'index.html'))) {
    throw new Error(`llms.txt points to an unbuilt page: ${url}`);
  }
}

writeFileSync(feed, content);
console.log(`Verified llms.txt routes; corrected ${rewritten} source-path links.`);
