/**
 * 教学用：模拟界面侧在提交前对字段做一层变换。
 * 真实项目逻辑通常在打包后的 app.*.js 中，需镜像到本地后再分析。
 */
function encodeForSubmit(plain) {
  const step = btoa(unescape(encodeURIComponent(plain)));
  return "DEMO:" + step;
}

if (typeof window !== "undefined") {
  window.encodeForSubmit = encodeForSubmit;
  console.log("[demo] encodeForSubmit('sample') =>", encodeForSubmit("sample"));
}
