import { readFile } from 'node:fs/promises';
import openapiTS, { astToString } from 'openapi-typescript';

const schema = new URL('../../contracts/openapi.json', import.meta.url);
const target = new URL('../src/shared/api/generated/schema.d.ts', import.meta.url);
const generated = astToString(await openapiTS(schema));
const current = await readFile(target, 'utf8');
// The CLI adds a generated-file header. Compare the actual declarations too.
const declarations = (text) => text.replace(/^\/\*\*[\s\S]*?\*\/\s*/, '').replace(/\r\n/g, '\n');
if (declarations(generated) !== declarations(current)) {
  console.error('TypeScript contract drift: run npm run api:generate');
  process.exitCode = 1;
} else {
  console.log('TypeScript client types match OpenAPI');
}
