/**
 * WorkCode Preview 伪造激活码生成器
 * 
 * 前提: 已运行 crack_workcode.js 让 verifySignature 返回 true
 * 使用方法:
 *   1. 运行 node forge_license.js <邮箱>
 *   2. 复制输出的激活码
 *   3. 在 WorkCode 登录弹窗输入对应邮箱 + 激活码
 *   4. 点击登录 → 直接通过
 */

function base64urlEncode(str) {
  return Buffer.from(str, 'utf8')
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

function generateLicense(email) {
  const now = Math.floor(Date.now() / 1000);
  const activeWindowDays = 365;
  const validDays = 365;
  const salt = 'workcode-salt-2024';
  
  // payload 格式: email|genTimestamp|activeWindowDays|validDays|salt
  const payload = `${email}|${now}|${activeWindowDays}|${validDays}|${salt}`;
  
  // 签名可以是任意值，因为 crack_workcode.js 已让 verifySignature 返回 true
  const signature = 'FORGED_SIGNATURE';
  
  // 激活码格式: base64url( signature + ":::" + payload )
  const raw = `${signature}:::${payload}`;
  const licenseCode = base64urlEncode(raw);
  
  return {
    email,
    payload,
    licenseCode
  };
}

const email = process.argv[2] || 'test@example.com';
const result = generateLicense(email);

console.log('='.repeat(60));
console.log(' WorkCode Preview 伪造激活码');
console.log('='.repeat(60));
console.log();
console.log('邮箱:', result.email);
console.log('Payload:', result.payload);
console.log();
console.log('激活码 (复制到登录框):');
console.log(result.licenseCode);
console.log();
console.log('='.repeat(60));
console.log('使用步骤:');
console.log('1. 确保已运行: node crack_workcode.js');
console.log('2. 启动 WorkCode Preview');
console.log('3. 在登录弹窗输入上述邮箱和激活码');
console.log('4. 点击登录 → 直接通过');
console.log('='.repeat(60));
