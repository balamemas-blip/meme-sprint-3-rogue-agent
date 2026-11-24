// Meme Sprint 3: AI Agent Goes Rogue — program/v1 entry.
//
// Reads the pre-built meme image (./entry.png, next to this file),
// validates it is a whole PNG within the gate limits, and copies it to
// the output directory as entry.png.
//
// Deterministic: no time, no randomness, no network, no environment
// secrets. Standard library only.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const MAX_BYTES = 1_048_576; // 1 MiB
const MAX_DIMENSION = 1024;

function fail(message: string): never {
  throw new Error(`entry.png rejected: ${message}`);
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const botDir = process.env.MAKEFUN_BOT_DIR
    ? resolve(process.env.MAKEFUN_BOT_DIR)
    : here;
  const outDir = process.env.MAKEFUN_OUTPUT_DIR
    ? resolve(process.env.MAKEFUN_OUTPUT_DIR)
    : "/output";

  const src = join(botDir, "entry.png");
  if (!existsSync(src)) fail(`missing ${src}`);

  const bytes = readFileSync(src);
  if (bytes.length > MAX_BYTES) {
    fail(`${bytes.length} bytes exceeds ${MAX_BYTES}`);
  }
  if (bytes.length < 33 || !bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    fail("not a PNG file (bad magic bytes)");
  }
  // IHDR: width at bytes 16-19, height at bytes 20-23, big-endian uint32.
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width === 0 || height === 0) fail("zero image dimension");
  if (width > MAX_DIMENSION || height > MAX_DIMENSION) {
    fail(`${width}x${height} exceeds ${MAX_DIMENSION}x${MAX_DIMENSION}`);
  }

  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  copyFileSync(src, dest);

  // Confirm what landed is exactly what was validated.
  const landed = statSync(dest);
  if (landed.size !== bytes.length) fail("output size mismatch");
  console.log(`wrote ${dest} (${width}x${height}, ${bytes.length} bytes)`);
}

main();
