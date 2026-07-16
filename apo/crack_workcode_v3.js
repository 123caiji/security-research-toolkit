/**
 * WorkCode Preview 激活码验证破解脚本 V3（修复版）
 * 修复了 V2 中 brace count 计算错误导致的代码残留问题
 */

const fs = require('fs');
const path = require('path');

const TARGET = path.join(
  __dirname,
  'WorkCode Preview',
  'resources',
  'app',
  'out',
  'renderer',
  'assets',
  'main-ocZkPq6k.js'
);

if (!fs.existsSync(TARGET)) {
  console.error('[!] 目标文件不存在:', TARGET);
  process.exit(1);
}

let patched = fs.readFileSync(TARGET, 'utf8');
let modified = false;

function replaceFunction(patched2, funcPrefix, newBody) {
  const idx = patched2.indexOf(funcPrefix);
  if (idx < 0) return { success: false, patched: patched2, reason: '未找到函数声明' };
  
  // 从函数声明的末尾开始计算 brace count（包含 { ）
  const start = idx + funcPrefix.length - 1; // 指向 {
  let braceCount = 1;
  let i = start + 1;
  for (; i < patched2.length; i++) {
    if (patched2[i] === '{') braceCount++;
    else if (patched2[i] === '}') {
      braceCount--;
      if (braceCount === 0) {
        i++; // 包含 }
        break;
      }
    }
  }
  const oldFunc = patched2.slice(idx, i);
  return { success: true, patched: patched2.replace(oldFunc, newBody) };
}

// === Patch 1: verifySignature ===
const r1 = replaceFunction(patched, 'async function verifySignature(payload, signature2) {', 
  'async function verifySignature(payload, signature2) { return true; }');
if (r1.success) {
  patched = r1.patched;
  console.log('[+] Patch 1 成功: verifySignature 已绕过');
  modified = true;
} else {
  console.log('[*] Patch 1 跳过:', r1.reason);
}

// === Patch 2: activateLicense ===
const r2 = replaceFunction(patched, 'async function activateLicense(email, licenseCode) {',
  `async function activateLicense(email, licenseCode) {
  const now2 = nowSeconds();
  return {
    ok: true,
    value: {
      email: normalizeEmail(email) || "cracked@local.com",
      licenseCode: normalizeLicenseCode(licenseCode || "CRACKED"),
      activatedAt: now2,
      validDays: 9999,
      expiresAt: now2 + 9999 * secondsPerDay,
      lastCheckedAt: now2
    }
  };
}`);
if (r2.success) {
  patched = r2.patched;
  console.log('[+] Patch 2 成功: activateLicense 已绕过');
  modified = true;
} else {
  console.log('[-] Patch 2 失败:', r2.reason);
}

// === Patch 3: verifyStoredLicense ===
const r3 = replaceFunction(patched, 'async function verifyStoredLicense(record2) {',
  `async function verifyStoredLicense(record2) {
  const now2 = nowSeconds();
  return {
    ok: true,
    value: {
      ...record2,
      expiresAt: record2.activatedAt + record2.validDays * secondsPerDay,
      lastCheckedAt: now2
    }
  };
}`);
if (r3.success) {
  patched = r3.patched;
  console.log('[+] Patch 3 成功: verifyStoredLicense 已绕过');
  modified = true;
} else {
  console.log('[-] Patch 3 失败:', r3.reason);
}

// === Patch 4: recordSeal ===
const r4 = replaceFunction(patched, 'async function recordSeal(record2) {',
  'async function recordSeal(record2) { return "cracked"; }');
if (r4.success) {
  patched = r4.patched;
  console.log('[+] Patch 4 成功: recordSeal 已固定');
  modified = true;
} else {
  console.log('[*] Patch 4 跳过:', r4.reason);
}

// === 写入 ===
if (modified) {
  const backup = TARGET + '.bak';
  if (!fs.existsSync(backup)) {
    fs.copyFileSync(TARGET, backup);
    console.log('[*] 原文件已备份到:', backup);
  }
  fs.writeFileSync(TARGET, patched, 'utf8');
  console.log();
  console.log('='.repeat(60));
  console.log(' V3 破解完成！');
  console.log('='.repeat(60));
  console.log();
  console.log(' 使用方法:');
  console.log(' 1. 关闭 WorkCode Preview');
  console.log(' 2. 重新打开 WorkCode Preview.exe');
  console.log(' 3. 在登录弹窗输入任意邮箱 + 任意激活码');
  console.log(' 4. 点击登录 → 直接通过，有效期 9999 天');
  console.log();
} else {
  console.log();
  console.log('[-] 未做任何修改');
}
