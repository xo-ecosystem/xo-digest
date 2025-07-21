import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PROJECT_ROOT = path.resolve(__dirname, "..");
const PACKAGE_JSON = path.join(PROJECT_ROOT, "package.json");
const LOG_FILE = path.join(PROJECT_ROOT, "ghost-deps.log");
const SEARCH_DIRS = ["src", "scripts", "hardhat", "public"];

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const removeUnused = args.includes("--remove-unused");

const contentFiles: string[] = [];

function collectFiles(dir: string) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      collectFiles(fullPath);
    } else if (entry.name.endsWith(".ts") || entry.name.endsWith(".js")) {
      contentFiles.push(fullPath);
    }
  }
}

function extractUsedModules(): Set<string> {
  const used = new Set<string>();
  const importRegex = /(?:import\s+(?:.*?\s+from\s+)?|require\()\s*['"]([^'"]+)['"]/g;
  for (const file of contentFiles) {
    const content = fs.readFileSync(file, "utf8");
    let match;
    while ((match = importRegex.exec(content)) !== null) {
      const mod = match[1];
      if (!mod.startsWith(".") && !mod.startsWith("/")) {
        const packageName = mod.startsWith("@")
          ? mod.split("/").slice(0, 2).join("/")
          : mod.split("/")[0];
        used.add(packageName);
      }
    }
  }
  return used;
}

function auditDependencies() {
  const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON, "utf8"));
  const deps = Object.keys(pkg.dependencies || {});
  const devDeps = Object.keys(pkg.devDependencies || {});

  SEARCH_DIRS.forEach((dir) => {
    const fullPath = path.join(PROJECT_ROOT, dir);
    if (fs.existsSync(fullPath)) collectFiles(fullPath);
  });

  const usedModules = extractUsedModules();
  const unusedDeps = deps.filter((dep) => !usedModules.has(dep));
  const unusedDevDeps = devDeps.filter((dep) => !usedModules.has(dep));

  const logLines = [];

  if (unusedDeps.length === 0 && unusedDevDeps.length === 0) {
    logLines.push("✅ No ghost dependencies found.");
  } else {
    if (unusedDeps.length) {
      logLines.push("🧹 Unused dependencies:");
      unusedDeps.forEach((dep) => logLines.push(`  - ${dep}`));
    }
    if (unusedDevDeps.length) {
      logLines.push("🧹 Unused devDependencies:");
      unusedDevDeps.forEach((dep) => logLines.push(`  - ${dep}`));
    }
  }

  const logOutput = logLines.join("\n");
  console.log(logOutput);
  fs.writeFileSync(LOG_FILE, logOutput + "\n");
  console.log(`📄 Report saved to ghost-deps.log`);

  if (removeUnused && (unusedDeps.length || unusedDevDeps.length)) {
    const removeCmd = `npm uninstall ${[...unusedDeps, ...unusedDevDeps].join(" ")}`;
    if (dryRun) {
      console.log("💡 Dry run mode: skipping uninstall.");
      console.log(`🧪 Would run: ${removeCmd}`);
    } else {
      console.log(`🚮 Removing unused dependencies...`);
      const { execSync } = require("child_process");
      execSync(removeCmd, { stdio: "inherit" });
    }
  }
}

auditDependencies();