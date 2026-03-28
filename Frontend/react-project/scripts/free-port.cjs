const { execSync } = require("node:child_process");

const port = process.env.PORT || "5173";

function getPidsUsingPort(targetPort) {
  try {
    const output = execSync(`netstat -ano | findstr :${targetPort}`, {
      stdio: ["ignore", "pipe", "ignore"],
      encoding: "utf8",
    });

    return [...new Set(
      output
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)
        .filter((line) => line.includes("LISTENING"))
        .map((line) => line.split(/\s+/).at(-1))
        .filter((pid) => pid && /^\d+$/.test(pid))
    )];
  } catch {
    return [];
  }
}

function killPid(pid) {
  try {
    execSync(`taskkill /PID ${pid} /F`, {
      stdio: ["ignore", "pipe", "pipe"],
      encoding: "utf8",
    });
    return true;
  } catch {
    return false;
  }
}

const pids = getPidsUsingPort(port);

if (pids.length === 0) {
  console.log(`[predev] Port ${port} is already free.`);
  process.exit(0);
}

for (const pid of pids) {
  const killed = killPid(pid);
  if (killed) {
    console.log(`[predev] Freed port ${port} by stopping PID ${pid}.`);
  } else {
    console.log(`[predev] Could not stop PID ${pid}. You may need to run terminal as Administrator.`);
  }
}

process.exit(0);
