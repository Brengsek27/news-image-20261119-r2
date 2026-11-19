import { copyFile, mkdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const imageUrl = new URL('./entry.png', import.meta.url);
const imagePath = fileURLToPath(imageUrl);
const image = await readFile(imagePath);
const signature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

if (image.length < signature.length || !image.subarray(0, signature.length).equals(signature)) {
  throw new Error('entry.png is not a valid PNG: invalid signature');
}
if (image.length > 1048576) {
  throw new Error(`entry.png exceeds the 1048576-byte limit (${image.length} bytes)`);
}
if (image.length < 24 || image.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png is not a valid PNG: IHDR chunk is missing');
}
if (image.readUInt32BE(8) !== 13) {
  throw new Error('entry.png is not a valid PNG: IHDR chunk must contain 13 bytes');
}
const width = image.readUInt32BE(16);
const height = image.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024x1024 (found ${width}x${height})`);
}

const outputDirectory = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const outputFile = join(outputDirectory, 'entry.png');
await mkdir(outputDirectory, { recursive: true });
await copyFile(imagePath, outputFile);
console.log(`Copied ${image.length} bytes to ${outputFile}`);

