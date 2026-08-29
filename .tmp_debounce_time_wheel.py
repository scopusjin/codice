from pathlib import Path

path = Path("app/native_time_picker_frontend/main.js")
text = path.read_text(encoding="utf-8")

old = '''let hourScrollTimer = null;\nlet minuteScrollTimer = null;\n'''
new = '''let hourScrollTimer = null;\nlet minuteScrollTimer = null;\nlet desktopWheelCommitTimer = null;\n'''
if text.count(old) != 1:
    raise SystemExit(f"timer anchor mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

old = '''function adjustByMinutes(delta) {\n  const normalized = normalizeTypedTime(timeInput.value) || committedValue;\n  const parsed = parseTime(normalized);\n  let total = parsed.hour * 60 + parsed.minute + delta;\n  total = ((total % 1440) + 1440) % 1440;\n  commitNormalizedValue(formatTime(Math.floor(total / 60), total % 60));\n}\n'''
new = '''function adjustByMinutes(delta, commit = true) {\n  const normalized = normalizeTypedTime(timeInput.value) || committedValue;\n  const parsed = parseTime(normalized);\n  let total = parsed.hour * 60 + parsed.minute + delta;\n  total = ((total % 1440) + 1440) % 1440;\n  const value = formatTime(Math.floor(total / 60), total % 60);\n\n  if (commit) {\n    commitNormalizedValue(value);\n  } else {\n    timeInput.value = value;\n  }\n}\n\nfunction scheduleDesktopWheelCommit() {\n  window.clearTimeout(desktopWheelCommitTimer);\n  desktopWheelCommitTimer = window.setTimeout(() => {\n    desktopWheelCommitTimer = null;\n    commitTypedValue();\n  }, 320);\n}\n'''
if text.count(old) != 1:
    raise SystemExit(f"adjust anchor mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

old = '''timeInput.addEventListener("blur", commitTypedValue);\n'''
new = '''timeInput.addEventListener("blur", () => {\n  window.clearTimeout(desktopWheelCommitTimer);\n  desktopWheelCommitTimer = null;\n  commitTypedValue();\n});\n'''
if text.count(old) != 1:
    raise SystemExit(f"blur anchor mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

old = '''timeInput.addEventListener("wheel", (event) => {\n  if (isMobile) {\n    return;\n  }\n  event.preventDefault();\n  adjustByMinutes(event.deltaY < 0 ? 5 : -5);\n}, { passive: false });\n'''
new = '''timeInput.addEventListener("wheel", (event) => {\n  if (isMobile) {\n    return;\n  }\n  event.preventDefault();\n  adjustByMinutes(event.deltaY < 0 ? 5 : -5, false);\n  scheduleDesktopWheelCommit();\n}, { passive: false });\n'''
if text.count(old) != 1:
    raise SystemExit(f"wheel anchor mismatch: {text.count(old)}")
text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")

updated = path.read_text(encoding="utf-8")
required = [
    "let desktopWheelCommitTimer = null;",
    "function scheduleDesktopWheelCommit()",
    "}, 320);",
    "adjustByMinutes(event.deltaY < 0 ? 5 : -5, false);",
    "scheduleDesktopWheelCommit();",
]
missing = [item for item in required if item not in updated]
if missing:
    raise SystemExit(f"missing expected changes: {missing}")
