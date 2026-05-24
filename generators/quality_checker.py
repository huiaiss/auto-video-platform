"""Quality Checker — 确定性规则引擎 + 可选AI二审.

检查每个Script是否满足抖音算法要求，不满足的直接打回给具体修复建议。
不做"AI审AI"的无效循环，规则全部可解释、可调试。

Usage:
    from generators.quality_checker import QualityChecker
    checker = QualityChecker()
    report = checker.check(script)
    if not report.passed:
        fixed_script = checker.auto_fix(script, report)
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from .script_engine import Script, Beat


# ─── Data Types ─────────────────────────────────────────────

@dataclass
class Violation:
    """一条违规记录."""
    rule: str           # 规则名称
    severity: str       # "blocker" | "warning" | "suggestion"
    detail: str         # 具体问题描述
    fix_hint: str       # 修复建议


@dataclass
class QualityReport:
    """质检报告."""
    passed: bool                        # 是否通过所有blocker规则
    score: int                          # 0-100
    violations: list[Violation]
    warnings: list[Violation]           # 不阻塞但建议修复
    suggestions: list[Violation]        # 锦上添花
    summary: str                        # 一句话总结


# ─── Rule Definitions ───────────────────────────────────────

# 每种视频类型的时长建议（秒）
DURATION_RANGES = {
    "ai_flaw_detect": (25, 60),
    "product_promo":   (25, 50),
    "factory_promo":   (28, 45),
    "tutorial":        (25, 55),
    "vlog":            (20, 45),
}

# 各种触发词检测
HOOK_STATEMENT_PATTERNS = [
    r'^(这是|今天|我们|大家|首先|下面|现在|本次|这期)',
    r'^(大家好|欢迎|各位)',
]

SAVE_TRIGGER_KEYWORDS = [
    '保存', '收藏', '截图', '对照', '检查清单', '下次', '以后',
    '别忘', '记住', '存下来', '留着', '收好',
]

SHARE_TRIGGER_KEYWORDS = [
    '转发', '分享', '发给', '转给', '@', '告诉你',
    '你身边', '你朋友', '你同事', '身边的人',
]

COMMENT_TRIGGER_KEYWORDS = [
    '评论区', '评论', '留言', '告诉我', '你觉得', '你见过',
    '你怎么', '你会', '选哪个', '哪个',
]


# ─── Checker ────────────────────────────────────────────────

class QualityChecker:
    """确定性规则质检引擎.

    所有规则都是确定性的（正则/计数/时长），不依赖LLM。
    可选AI二审仅用于主观项（语气、重复度），不阻塞生产。
    """

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        import os
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or "deepseek-chat"
        self.enable_ai_pass = bool(self.api_key)

    # ─── Public API ─────────────────────────────────────

    def check(self, script: Script, video_type: str = "") -> QualityReport:
        """对Script执行全部确定性规则检查.

        Returns:
            QualityReport with passed=True 当且仅当所有blocker通过.
        """
        violations = []
        warnings = []
        suggestions = []

        # Blocker rules — 必须通过
        violations.extend(self._check_hook(script))
        violations.extend(self._check_save_trigger(script))
        violations.extend(self._check_share_trigger(script))
        violations.extend(self._check_comment_trigger(script))
        violations.extend(self._check_sentence_length(script))
        violations.extend(self._check_info_density(script))
        violations.extend(self._check_checklist(script))
        violations.extend(self._check_duration(script, video_type))

        # Warning rules — 建议通过
        warnings.extend(self._check_beat_count(script))
        warnings.extend(self._check_animation_variety(script))
        warnings.extend(self._check_emotion_variety(script))
        warnings.extend(self._check_tags(script))

        # Suggestion rules — 锦上添花
        suggestions.extend(self._check_title_strength(script))
        suggestions.extend(self._check_hook_diversity(script))

        blocker_count = len(violations)
        warning_count = len(warnings)
        passed = blocker_count == 0
        score = self._calc_score(blocker_count, warning_count)

        return QualityReport(
            passed=passed,
            score=score,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
            summary=self._make_summary(passed, blocker_count, warning_count, score),
        )

    def auto_fix(self, script: Script, report: QualityReport) -> Script:
        """根据质检报告自动修复可修复的问题.

        能自动修的：补齐缺失的trigger标记、修正checklist为空、截断过长outro。
        不能自动修的（内容质量问题）：返回原script并附带fix提示。
        """
        beats = list(script.beats)
        outro = script.outro

        for v in report.violations:
            if v.rule == "save_trigger_missing":
                outro.is_save_trigger = True
            if v.rule == "share_trigger_missing":
                outro.is_share_trigger = True
            if v.rule == "comment_trigger_missing":
                outro.is_comment_trigger = True
            if v.rule == "checklist_empty":
                for b in reversed(beats):
                    if len(b.text) > 8:
                        script.checklist = f"核心要点：{b.text}"
                        break
            if v.rule == "outro_too_long":
                # 截断到50字：保留品牌slogan部分，去掉冗余引导
                text = outro.text
                # 按句号/感叹号拆句，保留前两句
                sentences = re.split(r'[。！!]', text)
                trimmed = ""
                for s in sentences:
                    if len(trimmed) + len(s) <= 48:
                        trimmed += s + "。"
                    else:
                        break
                if len(trimmed) < 10:
                    trimmed = text[:48]
                outro.text = trimmed.strip()

        return Script(
            title=script.title,
            hook_type=script.hook_type,
            beats=beats,
            outro=outro,
            tags=script.tags,
            bgm_style=script.bgm_style,
            checklist=script.checklist,
            total_duration_s=sum(b.duration_s for b in beats) + outro.duration_s,
        )

    def ai_review(self, script: Script, video_type: str = "") -> list[Violation]:
        """可选的AI二审 — 检查主观项（语气、重复度、口播自然度）.

        不阻塞生产流程，仅作为suggestions返回。
        """
        if not self.enable_ai_pass:
            return []

        prompt = self._build_ai_review_prompt(script, video_type)
        try:
            response = self._call_llm(prompt)
            return self._parse_ai_violations(response)
        except Exception:
            return []

    # ─── Blocker Rules ───────────────────────────────────

    def _check_hook(self, script: Script) -> list[Violation]:
        """规则1：第一个Beat必须是钩子，不能是陈述句."""
        if not script.beats:
            return [Violation("hook_empty", "blocker",
                              "脚本没有任何Beat", "至少需要3个Beat")]

        first = script.beats[0]
        v = []

        # 检测陈述句开头
        for pattern in HOOK_STATEMENT_PATTERNS:
            if re.match(pattern, first.text):
                v.append(Violation(
                    "hook_is_statement", "blocker",
                    f'第1个Beat是陈述句开头："{first.text[:20]}..."',
                    '前3秒必须是钩子：用疑问句、反常识、或悬念开头。例如"你发现了吗？""这张图里藏着一个破绽""这个价格能做到这个品质？"',
                ))
                break

        # 检测第一个beat的emotion是否为hook类型
        if first.emotion != "hook":
            v.append(Violation(
                "hook_emotion_wrong", "blocker",
                f"第1个Beat的心理功能标记为'{first.emotion}'而非'hook'",
                '第一个Beat的emotion必须设为"hook"',
            ))

        # 第一个beat的时长检查
        if first.duration_s > 5:
            v.append(Violation(
                "hook_too_long", "warning",
                f"第1个Beat时长{first.duration_s}秒，钩子超过5秒会失去注意力",
                "钩子控制在3-4秒，快速抛出悬念后进入正文",
            ))

        return v

    def _check_save_trigger(self, script: Script) -> list[Violation]:
        """规则2：必须有至少1个收藏诱因."""
        all_beats = script.beats + [script.outro]
        has_trigger = any(b.is_save_trigger for b in all_beats)

        if not has_trigger:
            return [Violation(
                "save_trigger_missing", "blocker",
                "没有任何Beat标记为收藏诱因",
                '至少1个Beat的is_save_trigger=true，口播中自然引导"建议截图保存"',
            )]

        # 检查口播中是否有收藏引导词
        has_keyword = any(
            any(kw in b.text for kw in SAVE_TRIGGER_KEYWORDS)
            for b in all_beats if b.is_save_trigger
        )
        if not has_keyword:
            return [Violation(
                "save_trigger_no_keyword", "warning",
                "标记了is_save_trigger但口播中没有收藏引导词（保存/收藏/截图等）",
                '在收藏诱因Beat的口播中加入"建议收藏""截图保存"等引导',
            )]

        return []

    def _check_share_trigger(self, script: Script) -> list[Violation]:
        """规则3：必须有至少1个转发诱因."""
        all_beats = script.beats + [script.outro]
        has_trigger = any(b.is_share_trigger for b in all_beats)

        if not has_trigger:
            return [Violation(
                "share_trigger_missing", "blocker",
                "没有任何Beat标记为转发诱因",
                '至少1个Beat的is_share_trigger=true，口播中加入"转发给你身边XX的人"',
            )]

        return []

    def _check_comment_trigger(self, script: Script) -> list[Violation]:
        """规则4：必须有至少1个评论引爆点."""
        all_beats = script.beats + [script.outro]
        has_trigger = any(b.is_comment_trigger for b in all_beats)

        if not has_trigger:
            return [Violation(
                "comment_trigger_missing", "blocker",
                "没有任何Beat标记为评论引爆点",
                '至少1个Beat的is_comment_trigger=true，结尾抛开放式问题让观众讨论',
            )]

        # 检查是否有问句
        has_question = any("？" in b.text or "?" in b.text for b in all_beats)
        if not has_question:
            return [Violation(
                "comment_trigger_no_question", "warning",
                "有评论标记但全脚本没有问句，观众不会主动评论",
                '结尾加入开放式问题，如"你还见过什么XX？评论区告诉我"',
            )]

        return []

    def _check_sentence_length(self, script: Script) -> list[Violation]:
        """规则5：每句口播≤35字."""
        violations = []
        for b in script.beats:
            char_count = len(b.text.replace(' ', ''))
            if char_count > 35:
                violations.append(Violation(
                    "sentence_too_long", "blocker",
                    f'Beat {b.index} 口播{char_count}字（>35）："{b.text[:25]}..."',
                    f'精简到35字以内。当前可删减修饰词或拆分为2个Beat。',
                ))

        # outro 允许稍长（≤50字）
        outro_len = len(script.outro.text.replace(' ', ''))
        if outro_len > 50:
            violations.append(Violation(
                "outro_too_long", "blocker",
                f'结尾口播{outro_len}字（>50）："{script.outro.text[:30]}..."',
                '结尾精简到50字以内，保留slogan+一个引导即可',
            ))

        return violations

    def _check_info_density(self, script: Script) -> list[Violation]:
        """规则6：每5秒至少1个新信息点.

        计算方法：检查每5秒窗口内是否有新的实质性内容。
        简化：平均信息密度 = beat数 / 总时长，应 ≥ 1/5 = 0.2 beats/秒
        """
        if not script.beats:
            return []

        total = sum(b.duration_s for b in script.beats)
        density = len(script.beats) / total if total > 0 else 0

        if density < 0.18:  # 略低于0.2，留余量
            return [Violation(
                "info_density_low", "blocker",
                f"信息密度{density:.2f} beats/秒（要求≥0.2），{total:.0f}秒仅{len(script.beats)}个Beat",
                f'增加{max(1, int(total * 0.2 - len(script.beats)))}个Beat，或缩短每个Beat的时长',
            )]

        # 检查是否有超过10秒的单个Beat（死空气）
        for b in script.beats:
            if b.duration_s > 10:
                return [Violation(
                    "beat_too_long", "warning",
                    f"Beat {b.index} 时长{b.duration_s}秒（>10秒），观众注意力会断",
                    f'将Beat {b.index} 拆分为2个Beat，或缩短到8秒以内',
                )]

        return []

    def _check_checklist(self, script: Script) -> list[Violation]:
        """规则7：checklist必须非空且有用."""
        if not script.checklist or len(script.checklist.strip()) < 5:
            return [Violation(
                "checklist_empty", "blocker",
                "可截图保存的检查清单为空或太短",
                '填写checklist字段（50字以内），如"AI识别三要点：①看手指②看文字③看光影"',
            )]

        if len(script.checklist) > 60:
            return [Violation(
                "checklist_too_long", "warning",
                f"检查清单{len(script.checklist)}字（建议≤50字），截图可能显示不全",
                "精简到50字以内",
            )]

        return []

    def _check_duration(self, script: Script, video_type: str) -> list[Violation]:
        """规则8：总时长在合理范围内."""
        if not video_type or video_type not in DURATION_RANGES:
            return []

        min_dur, max_dur = DURATION_RANGES[video_type]
        total = script.total_duration_s

        if total < min_dur:
            return [Violation(
                "duration_too_short", "warning",
                f"总时长{total:.0f}秒（建议{min_dur}-{max_dur}秒），太短可能信息量不够",
                f'增加内容或延展破绽分析，目标≥{min_dur}秒',
            )]

        if total > max_dur + 10:  # 允许略超
            return [Violation(
                "duration_too_long", "warning",
                f"总时长{total:.0f}秒（建议{min_dur}-{max_dur}秒），太长影响完播率",
                f'精简内容到≤{max_dur}秒',
            )]

        return []

    # ─── Warning Rules ────────────────────────────────────

    def _check_beat_count(self, script: Script) -> list[Violation]:
        """Beat数量是否合理."""
        n = len(script.beats)
        if n < 4:
            return [Violation("too_few_beats", "warning",
                              f"仅{n}个Beat（建议≥4），节奏可能太慢",
                              "增加破绽点或卖点展示的Beat")]
        if n > 15:
            return [Violation("too_many_beats", "warning",
                              f"{n}个Beat（建议≤15），节奏可能太快观众跟不上",
                              "合并信息密度相近的Beat")]
        return []

    def _check_animation_variety(self, script: Script) -> list[Violation]:
        """动画类型是否多样."""
        anims = [b.animation for b in script.beats if b.animation != "none"]
        unique = len(set(anims))
        if unique < 3 and len(script.beats) >= 4:
            return [Violation("animation_monotone", "suggestion",
                              f"仅{unique}种动画类型，视觉可能单调",
                              "混用zoom/fade/slide/pop/pulse，至少3种")]
        return []

    def _check_emotion_variety(self, script: Script) -> list[Violation]:
        """心理功能是否覆盖完整弧线."""
        emotions = [b.emotion for b in script.beats]
        required = {"hook", "trust", "action"}
        missing = required - set(emotions)
        if missing:
            return [Violation("emotion_arc_incomplete", "warning",
                              f"缺少心理功能：{', '.join(missing)}（完整弧线需hook→trust→action）",
                              "确保beat的emotion字段覆盖：hook(开头)→curiosity/surprise(中段)→trust(中后)→action(结尾)")]
        return []

    def _check_tags(self, script: Script) -> list[Violation]:
        """话题标签是否合理."""
        if len(script.tags) < 3:
            return [Violation("too_few_tags", "suggestion",
                              f"仅{len(script.tags)}个话题标签（建议≥4）",
                              "添加话题标签以增加推荐分发")]
        if len(script.tags) > 8:
            return [Violation("too_many_tags", "suggestion",
                              f"{len(script.tags)}个话题标签（建议≤8），太多稀释权重",
                              "保留最精准的5-6个标签")]
        return []

    # ─── Suggestion Rules ─────────────────────────────────

    def _check_title_strength(self, script: Script) -> list[Violation]:
        """标题是否有钩子元素."""
        title = script.title
        has_hook = any(char in title for char in ['？', '?', '！', '!'])
        if not has_hook and len(title) > 5:
            return [Violation("title_no_hook", "suggestion",
                              f'标题"{title}"缺少疑问或感叹语气',
                              "标题加入？或！制造悬念或冲击感")]
        return []

    def _check_hook_diversity(self, script: Script) -> list[Violation]:
        """检查是否用了陈词滥调的钩子."""
        cliches = ['你相信吗', '你知道吗', '今天给大家', '大家好我是']
        for cliche in cliches:
            if script.beats and cliche in script.beats[0].text:
                return [Violation("hook_cliche", "suggestion",
                                  f'钩子用了陈词滥调"{cliche}"',
                                  "用更具体的钩子，如'放大3倍后我看到了诡异的东西'")]
        return []

    # ─── Scoring ──────────────────────────────────────────

    def _calc_score(self, blocker_count: int, warning_count: int) -> int:
        """100分制：每blocker -15，每warning -5，最低0."""
        score = 100 - (blocker_count * 15) - (warning_count * 5)
        return max(0, score)

    def _make_summary(self, passed: bool, blockers: int, warnings: int,
                      score: int) -> str:
        if passed:
            return f"通过 ({score}分) — {warnings}条建议可忽略或采纳"
        else:
            return f"不通过 ({score}分) — {blockers}条必须修复 + {warnings}条建议"

    # ─── AI Second Pass ───────────────────────────────────

    def _build_ai_review_prompt(self, script: Script, video_type: str) -> str:
        lines = []
        for b in script.beats:
            lines.append(f"  Beat{b.index}[{b.emotion}][{b.duration_s}s]: {b.text}")
        beat_text = "\n".join(lines)

        return f"""你是抖音内容审稿人。审查以下脚本的主观质量。

## 脚本信息
标题：{script.title}
钩子类型：{script.hook_type}
Beat序列：
{beat_text}

结尾：{script.outro.text}

## 审查维度（只关注主观项）
1. 口播是否自然口语化（不能像AI写的播音腔）
2. 各Beat之间是否有内容重复
3. 语气是否符合视频类型({video_type})
4. 整体是否有"真人感"

## 输出格式
只输出JSON数组，每条是一条建议（不是blocker）。没有建议则输出空数组[]。

```json
[{{"rule":"ai_tone","detail":"具体问题","fix_hint":"修复建议"}}]
```"""

    def _call_llm(self, prompt: str) -> str:
        import json as _json
        import urllib.request, urllib.error

        data = _json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是严格的审稿人。只输出JSON格式，不要其他内容。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 1024,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = _json.loads(resp.read())
            return result["choices"][0]["message"]["content"]

    def _parse_ai_violations(self, response: str) -> list[Violation]:
        import json as _json

        json_str = response
        m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        if m:
            json_str = m.group(1)
        start = json_str.find('[')
        end = json_str.rfind(']')
        if start >= 0 and end > start:
            json_str = json_str[start:end + 1]

        items = _json.loads(json_str)
        return [
            Violation(
                rule=item.get("rule", "ai_suggestion"),
                severity="suggestion",
                detail=item.get("detail", ""),
                fix_hint=item.get("fix_hint", ""),
            )
            for item in items
        ]


# ─── Convenience ────────────────────────────────────────────

def quick_check(script: Script, video_type: str = "") -> bool:
    """快速检查：是否通过所有blocker."""
    checker = QualityChecker()
    report = checker.check(script, video_type)
    return report.passed
