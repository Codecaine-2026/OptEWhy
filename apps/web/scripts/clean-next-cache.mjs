import { rm } from "node:fs/promises";
import { resolve } from "node:path";

const nextCachePath = resolve(".next-cache");

await rm(nextCachePath, { force: true, recursive: true });
