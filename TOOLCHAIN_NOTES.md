# 工具链说明

本工程已合入天狐工具箱已解压目录中的核心工具资源：

- `tools/`
- `config/`
- `core/`
- `Java_path/`
- `notepad/`

外部压缩包、宣传图片和视频未复制。当前工程仍以 `config.json` 作为安全边界配置；天狐自身清单在 `config/tools.json`。

## 使用顺序

1. 先读 `.cursor/rules/bilingual-master-governance.mdc`
2. 再读 `.cursor/rules/user-governance-priority.mdc`
3. 再读 `.cursor/rules/overall-security-toolchain.mdc`
4. 按任务加载 `.cursor/skills/project-security-router/SKILL.md`
5. 需要工具时查 `.cursor/skills/local-toolbox-index/SKILL.md`
6. 需要方法论时查 `hack-skills/skills/hack/SKILL.md`
7. 扩大授权测试范围时按 `.cursor/rules/scope-expansion-authorization.mdc` 记录范围与配置

## 解释器

- Python：`python3/python.exe`
- Java 8：`Java_path/Java_8_win/bin/java.exe`
- Java 11：`Java_path/Java_11_win/bin/java.exe`

## 边界

真实目标扫描、爆破、漏洞利用必须有明确授权，并调整 `config.json`。默认只做本地模拟、静态分析和防御验证。
