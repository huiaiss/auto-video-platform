"""Script Generator — analysis report + config → LLM → structured production script.

Supports: Claude API, DeepSeek, or template-based fallback (offline mode).
Output: titles, hook, storyboard, BGM recommendations, tags, publish strategy.
"""
import json, os, re, yaml
from typing import Optional


class ConfigLoader:
    """Load and validate YAML configurations."""

    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "configs"
        )

    def load_video_type(self, type_name: str) -> dict:
        # Try both underscore and hyphen forms
        for name in (type_name, type_name.replace("-", "_"), type_name.replace("_", "-")):
            path = os.path.join(self.config_dir, "video_types", f"{name}.yaml")
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    return yaml.safe_load(f)
        path = os.path.join(self.config_dir, "video_types", f"{type_name}.yaml")
        raise FileNotFoundError(f"Config not found: {path}")

    def load_brand(self, brand_name: str) -> Optional[dict]:
        path = os.path.join(self.config_dir, "brands", f"{brand_name}.yaml")
        if not os.path.exists(path):
            return None
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)


class ScriptGenerator:
    """Generate structured production scripts from asset analysis reports."""

    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or os.environ.get("SCRIPT_MODEL", "deepseek-chat")
        self._config_loader = ConfigLoader()

    # ─── Public API ───────────────────────────────────────

    def generate(self, analysis_report: dict, video_type: str,
                 brand_name: str = None) -> dict:
        """
        Main entry: analysis JSON + config → structured production script.

        Returns dict with: titles, hook, storyboard, voiceover, bgm,
                          post_production, tags, publish_strategy
        """
        config = self._config_loader.load_video_type(video_type)
        brand = self._config_loader.load_brand(brand_name) if brand_name else None

        prompt = self._build_prompt(analysis_report, config, brand)

        # Try LLM, fall back to template
        try:
            response = self._call_llm(prompt)
            script = self._parse_response(response, config)
        except Exception as e:
            print(f"[ScriptGenerator] LLM failed ({e}), using template fallback.")
            script = self._template_fallback(analysis_report, config, brand)

        # Post-process: merge brand defaults, fill missing fields
        script = self._post_process(script, config, brand)
        return script

    # ─── Prompt building ──────────────────────────────────

    def _build_prompt(self, report: dict, config: dict, brand: Optional[dict]) -> str:
        """Build a detailed prompt from analysis data and config."""

        # Summarize the analysis report for the LLM
        findings_summary = self._summarize_findings(report)
        structure = config.get("structure", {})
        persona = config.get("script", {}).get("persona", "")
        hook_patterns = config.get("script", {}).get("hook_patterns", [])
        outro = config.get("script", {}).get("outro_line", "")

        brand_section = ""
        if brand:
            brand_section = f"""
品牌信息：
- 品牌名：{brand.get('brand', '')}
- 行业：{brand.get('industry', '')}
- 标语：{brand.get('tagline', '')}
- 必须提及：{brand.get('content_rules', {}).get('must_mention', [])}
- 语气：{brand.get('voice_identity', {}).get('tone', '')}
"""

        return f"""你是一位{persona}

{brand_section}

## 素材分析结果
{findings_summary}

## 视频结构要求
- 开场钩子：{structure.get('hook', 3)}秒 → 展示原图，制造悬念
- 核心展示（破绽放大）：选取3-5个最有代表性的破绽，每个5-8秒 → 逐个放大并用红圈标注
- 真vs假对比：{structure.get('compare', 8)}秒 → 并排展示AI图和真实照片的差异
- 总结：{structure.get('summary', 7)}秒 → 教观众记住检查要点
- 结尾引导：{structure.get('cta', structure.get('outro', 5))}秒

## 可选开场钩子模板
{chr(10).join(f'- "{p}"' for p in hook_patterns[:3])}

## 结尾口号
"{outro}"

## ⚠️ 关键要求（必须遵守）
1. **每个破绽放大镜头必须引用具体的乱码文字**，例如口播要说"招牌上写的'农时惠'三个字根本不通顺"，而不是"这里有文字乱码"。素材分析结果中每个finding的details字段包含检测到的具体文字，必须用上。
2. **从不同素材图片中选取破绽**，不要全从同一张图取。至少覆盖2-3张不同的图片。
3. **优先选有趣/搞笑的乱码文字**作为口播素材，例如'氽骶雠'、'床衷师珲'、'我衷薹清雾鄢诊绑湾'这种完全不通的假字效果最好。
4. 产生3个备选标题（悬念型、反常识型、教学型各1个）
5. 每句口播不超过{config.get('script', {}).get('max_words_per_shot', 35)}字
6. 推荐BGM风格和3首参考曲目
7. 给出后期制作建议

请用以下JSON格式回复（只输出JSON，不要有其他文字）：
```json
{{
  "titles": [
    {{"type": "悬念型", "text": "..."}},
    {{"type": "反常识型", "text": "..."}},
    {{"type": "教学型", "text": "..."}}
  ],
  "hook": {{
    "type": "悬念好奇 / 视觉冲击 / 反差对比 / 身份认同 / 痛点解决 / 反常识",
    "visual": "开场画面描述",
    "audio": "开场口播（口语化，有冲击力）",
    "text": "画面叠加文字",
    "duration_s": {structure.get('hook', 3)}
  }},
  "storyboard": [
    {{
      "shot": 1,
      "duration": "Xs",
      "visual": "画面描述（必须含坐标，如'放大(269,766)区域'）",
      "audio": "口播文案（必须引用具体的乱码文字）",
      "caption": "字幕文案"
    }}
  ],
  "bgm": {{
    "style": "音乐风格",
    "bpm": "BPM范围",
    "recommendations": ["曲目1", "曲目2", "曲目3"],
    "search_keywords": ["搜索词1", "搜索词2"]
  }},
  "post_production": {{
    "editing": {{"pace": "快节奏/中速/慢节奏", "transitions": "转场类型", "key_moments": "关键时间节点"}},
    "color_grading": {{"style": "调色风格", "parameters": "具体参数"}},
    "captions": {{"font": "字体", "style": "字幕样式", "animation": "动画效果"}},
    "sound_design": {{"sfx": "音效建议", "audio_mixing": "混音方案"}}
  }},
  "tags": {{
    "core": ["核心词1", "核心词2"],
    "trending": ["热搜词1", "热搜词2"],
    "long_tail": ["长尾词1", "长尾词2"]
  }}
}}
```"""

    def _summarize_findings(self, report: dict) -> str:
        """Convert analysis report into a concise text summary for the LLM.

        Extracts specific garbled text samples and coordinates so the LLM
        can write scripts that reference actual detected flaws, not generic labels.
        """
        lines = []

        # Handle both single scan and batch results
        results = report.get("results", [report])

        for r in results:
            img = r.get("image", "unknown")
            lines.append(f"\n### 素材: {img}")

            quality_notes = []
            flaw_notes = []
            garbled_samples = []  # Collect specific garbled text for LLM to use

            for d in r.get("detector_results", []):
                findings = d.get("findings", [])
                if d.get("error"):
                    continue
                if not findings:
                    continue

                detector = d["detector"]
                for f in findings[:5]:  # Top 5 per detector
                    line = f"  - [{detector}] [{f['severity']}] {f['desc']} (score={f['score']:.2f}): {f['details']}"
                    if detector in ("sharpness", "color", "composition", "stability"):
                        quality_notes.append(line)
                    else:
                        flaw_notes.append(line)

                    # Extract garbled text strings for the LLM to use in narration
                    if detector == "text":
                        detail = f.get("details", "")
                        # Parse out the detected text from format: "OCR置信度X.XX，检测到'...'"
                        import re as _re
                        match = _re.search(r"检测到'([^']*)'", detail)
                        if match and match.group(1).strip():
                            garbled_samples.append({
                                "text": match.group(1).strip(),
                                "cx": f.get("cx", 0),
                                "cy": f.get("cy", 0),
                                "score": f.get("score", 0),
                            })

            if quality_notes:
                lines.append("  质量检测：")
                lines.extend(quality_notes)
            if flaw_notes:
                lines.append("  破绽检测：")
                lines.extend(flaw_notes)

            # Top findings
            if r.get("top_findings"):
                lines.append("  最值得展示的画面/破绽（按分数排序）：")
                for tf in r["top_findings"][:5]:
                    lines.append(f"  - [{tf.get('detector', '?')}] score={tf['score']:.2f} {tf['desc']} @ ({tf['cx']},{tf['cy']})")

            # Garbled text summary — the key info for the LLM
            if garbled_samples:
                # Deduplicate and pick most interesting ones
                seen = set()
                unique_samples = []
                for g in garbled_samples:
                    if g["text"] not in seen and len(g["text"]) >= 2:
                        seen.add(g["text"])
                        unique_samples.append(g)
                if unique_samples:
                    samples_str = "、".join(
                        f"'{s['text']}'@({s['cx']},{s['cy']})"
                        for s in unique_samples[:8]
                    )
                    lines.append(f"  ⚠️ 具体乱码文字（口播必须引用）: {samples_str}")

        return "\n".join(lines)

    # ─── LLM call ─────────────────────────────────────────

    def _call_llm(self, prompt: str) -> str:
        """Call LLM API (supports OpenAI-compatible endpoints)."""
        import urllib.request, urllib.error

        # Determine if we should use Anthropic or OpenAI-compatible API
        if "anthropic" in self.base_url.lower() or self.api_key and self.api_key.startswith("sk-ant"):
            return self._call_claude(prompt)
        else:
            return self._call_openai_compatible(prompt)

    def _call_openai_compatible(self, prompt: str) -> str:
        """Call OpenAI-compatible API (DeepSeek, etc.)."""
        import urllib.request, urllib.error

        data = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的视频脚本撰写专家。请严格按照JSON格式回复。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "max_tokens": 4096,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"API HTTP {e.code}: {e.read().decode()[:500]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"API unreachable: {e.reason}")

    def _call_claude(self, prompt: str) -> str:
        """Call Anthropic Claude API."""
        import urllib.request, urllib.error

        data = json.dumps({
            "model": self.model or "claude-sonnet-4-6",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=data,
            headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read())
                return result["content"][0]["text"]
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Claude API HTTP {e.code}: {e.read().decode()[:500]}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Claude API unreachable: {e.reason}")

    # ─── Response parsing ─────────────────────────────────

    def _parse_response(self, response: str, config: dict) -> dict:
        """Extract JSON from LLM response (handles markdown code fences)."""
        # Try to find JSON in code blocks first
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', response, re.DOTALL)
        json_str = json_match.group(1) if json_match else response

        # Strip any leading/trailing non-JSON content
        json_str = json_str.strip()
        if not json_str.startswith('{'):
            # Find the first { and last }
            start = json_str.find('{')
            end = json_str.rfind('}')
            if start >= 0 and end > start:
                json_str = json_str[start:end + 1]

        return json.loads(json_str)

    # ─── Template fallback (offline mode) ─────────────────

    def _template_fallback(self, report: dict, config: dict, brand: Optional[dict]) -> dict:
        """Generate a basic script without LLM, driven entirely by the YAML config."""
        vt = config.get("type", "")
        structure = config.get("structure", {})
        findings = self._extract_top_findings(report)
        script_cfg = config.get("script", {})
        platforms = config.get("platforms", {})
        brand_name = brand.get("brand", "品牌") if brand else "产品"

        # Pick template strategy based on video type
        if vt == "ai-flaw-detect":
            return self._fallback_ai_flaw(findings, config, brand_name)
        else:
            return self._fallback_enterprise(findings, config, brand_name)

    def _fallback_ai_flaw(self, findings: list, config: dict, brand_name: str) -> dict:
        """Template for AI flaw detection / science videos.

        Uses specific garbled text from findings so even the fallback is
        informative — no more generic "文字乱码 at (269,766)" narrations.
        """
        structure = config.get("structure", {})
        script_cfg = config.get("script", {})
        platforms = config.get("platforms", {})

        # Only use flaw-relevant findings (face, hand, text, texture)
        flaw_findings = [f for f in findings
                         if f.get("detector") in ("face", "hand", "text", "texture")
                         and f.get("severity") in ("high", "medium")]

        # Diversify: pick at most 2 per image, up to 5 total
        seen_imgs = {}
        diverse = []
        for f in flaw_findings:
            img = f.get("_image", "")
            if img not in seen_imgs:
                seen_imgs[img] = 0
            if seen_imgs[img] >= 2:
                continue
            seen_imgs[img] += 1
            diverse.append(f)
            if len(diverse) >= 5:
                break

        storyboard = []
        outro_line = script_cfg.get("outro_line") or f"关注{brand_name}，下次被骗的不是你"

        def _extract_garbled_text(finding: dict) -> str:
            """Extract the actual garbled characters from a finding's details field."""
            import re as _re
            detail = finding.get("details", "")
            match = _re.search(r"检测到'([^']*)'", detail)
            if match and match.group(1).strip():
                return match.group(1).strip()
            return finding.get("desc", "异常")

        # Shot 1: Hook
        flaw_types = list({f["desc"] for f in diverse})
        flaw_summary = "、".join(flaw_types[:3])
        # Pick one juicy garbled text for the hook
        juicy = next((_extract_garbled_text(f) for f in diverse
                      if _extract_garbled_text(f) and len(_extract_garbled_text(f)) >= 2), None)
        hook_detail = f"比如'{juicy}'这种根本不通的假字" if juicy else f"{flaw_summary}全是破绽"
        storyboard.append({
            "shot": 1, "duration": f"{structure.get('hook', 3)}s",
            "visual": "AI生成图片完整展示（保持神秘感）",
            "audio": f"这张图看起来很正常对吧？放大3倍后你会发现{hook_detail}",
            "caption": "🔍 这张图有问题，你看出来了吗？",
        })

        # Shots 2-N: Each flaw with specific garbled text
        shot_num = 1
        for f in diverse:
            shot_num += 1
            detector = f.get("detector", "")
            detector_icon = {"face": "👤", "hand": "✋", "text": "📝", "texture": "🎨"}.get(detector, "🔍")
            garbled = _extract_garbled_text(f)
            img_name = f.get("_image", "")

            if detector == "text" and garbled and len(garbled) >= 2:
                # For text flaws: reference the specific garbled characters
                audio = f"先看{img_name}的{f['desc']}——AI写的是'{garbled}'，根本不成词，这是典型的AI乱码"
                caption = f"{detector_icon} 破绽{shot_num-1}: AI写成了'{garbled}'"
            elif detector == "text":
                audio = f"先看{img_name}的{f['desc']}——{f['details']}，明显是AI生成的痕迹"
                caption = f"{detector_icon} 破绽{shot_num-1}: {f['desc']}"
            elif detector in ("face", "hand"):
                audio = f"再看{img_name}的{f['desc']}——{f['details']}，真人不会有这种问题"
                caption = f"{detector_icon} 破绽{shot_num-1}: {f['desc']} ({f['details'][:20]})"
            else:
                audio = f"再看{img_name}的{f['desc']}——{f['details']}，典型的AI生成痕迹"
                caption = f"{detector_icon} 破绽{shot_num-1}: {f['desc']}"

            storyboard.append({
                "shot": shot_num, "duration": "6s",
                "visual": f"放大{f['desc']}区域 ({f.get('cx', 0)},{f.get('cy', 0)})，红色圆圈脉冲标注",
                "audio": audio,
                "caption": caption,
            })

        # Compare shot
        shot_num += 1
        storyboard.append({
            "shot": shot_num, "duration": f"{structure.get('compare', 10)}s",
            "visual": "左半屏AI假图 vs 右半屏真实照片对比",
            "audio": "对比一下，左边AI生成的文字全是乱码，右边真实照片的文字清晰可读。学会了吗？",
            "caption": "左边AI生成 ❌  |  右边真实照片 ✓",
        })

        # Summary
        shot_num += 1
        # Collect garbled texts for summary
        garbled_texts = [_extract_garbled_text(f) for f in diverse
                         if _extract_garbled_text(f) and len(_extract_garbled_text(f)) >= 2]
        summary_detail = "、".join(garbled_texts[:4]) if garbled_texts else flaw_summary
        storyboard.append({
            "shot": shot_num, "duration": f"{structure.get('summary', 10)}s",
            "visual": "破绽检查清单叠加（文字动画弹出）",
            "audio": f"总结一下：AI生成的文字像'{summary_detail}'这些全是乱码——记住这{len(diverse)}个特征，下次直接对照检查",
            "caption": f"✅ 检查清单：{flaw_summary}",
        })

        # Outro
        shot_num += 1
        storyboard.append({
            "shot": shot_num, "duration": f"{structure.get('outro', 7)}s",
            "visual": "黑底+品牌Logo+关注引导动画",
            "audio": outro_line,
            "caption": outro_line,
        })

        titles = [
            {"type": "悬念型", "text": f"这张图里藏着{len(diverse)}个破绽，你能找到几个？"},
            {"type": "反常识型", "text": f"AI连{list(flaw_types)[0] if flaw_types else '手指'}都画不好？放大看真相"},
            {"type": "教学型", "text": f"{len(diverse)}秒学会识别AI假图——{flaw_summary}鉴定法"},
        ]

        return {
            "titles": titles,
            "hook": {
                "type": "悬念好奇",
                "visual": storyboard[0]["visual"],
                "audio": storyboard[0]["audio"],
                "text": storyboard[0]["caption"],
                "duration_s": structure.get("hook", 3),
            },
            "storyboard": storyboard,
            "bgm": {
                "style": "赛博朋克 / 科技悬疑电子",
                "bpm": "110-130",
                "recommendations": ["Suspense Investigation", "Cyber Detective", "Digital Suspense"],
                "search_keywords": ["悬疑", "科技", "电子", "赛博朋克", "侦探"],
            },
            "post_production": {
                "editing": {"pace": "快节奏硬切", "transitions": "硬切为主，破绽出现时加速缩放", "key_moments": "0s悬念钩子, 3s第一次放大, 每6s一个新破绽, 最后5s总结"},
                "color_grading": {"style": "暗色背景+荧光绿/红色标注", "parameters": "背景压暗-15, 标注色#00e676荧光绿和#ff1744脉冲红"},
                "captions": {"font": "Noto Sans SC Bold", "style": "白字黑描边+关键词荧光绿高亮", "animation": "逐字弹出+破绽词放大"},
                "sound_design": {"sfx": "每次标注破绽时'叮'一声提示音", "audio_mixing": "人声-6dB, BGM-20dB, 提示音-8dB"},
            },
            "tags": {
                "core": (platforms.get("douyin", {}).get("hashtags", ["AI识别", "真假辨别"]))[:3],
                "trending": ["AI真假辨别", "防骗指南", "AI鉴定"],
                "long_tail": ["AI破绽", "如何识别AI图片", "AI造假"],
            },
            "voiceover": self._voiceover_config(config),
        }

    def _fallback_enterprise(self, findings: list, config: dict, brand_name: str) -> dict:
        """Template for enterprise promo videos."""
        structure = config.get("structure", {})
        script_cfg = config.get("script", {})
        outro_line = script_cfg.get("outro_line", "了解更多请私信")

        # Use quality findings for enterprise — show best parts
        quality_ok = [f for f in findings
                      if f.get("detector") in ("sharpness", "color", "composition")
                      and f.get("severity") == "low"]

        storyboard = []

        # Hook
        storyboard.append({
            "shot": 1, "duration": f"{structure.get('hook', 3)}s",
            "visual": f"{brand_name}最佳角度展示，配品牌色渐变背景",
            "audio": f"一台好的{brand_name}应该是什么样的？带你去工厂看看",
            "caption": f"{brand_name} | 源头工厂实拍",
        })

        # Showcase
        storyboard.append({
            "shot": 2, "duration": f"{structure.get('showcase', 15)}s",
            "visual": f"产线运转实拍 → {brand_name}多角度特写 → 细节放大",
            "audio": f"从原材料到成品，每一道工序都在这里完成。注意看这个细节——{brand_name}的品质就藏在这些看不见的地方",
            "caption": f"全自动生产线 | {brand_name}",
        })

        # Features
        storyboard.append({
            "shot": 3, "duration": f"{structure.get('features', 8)}s",
            "visual": f"{brand_name}关键参数字幕叠加+产品细节特写",
            "audio": f"精度控制在0.01mm以内，效率提升300%，这就是{brand_name}的核心竞争力",
            "caption": "精度±0.01mm | 效率+300% | 稳定运行5000h",
        })

        # Trust proof
        storyboard.append({
            "shot": 4, "duration": f"{structure.get('proof', 7)}s",
            "visual": "客户工厂实拍 / 出货照片 / 质检证书",
            "audio": f"已经服务超过100家企业，{brand_name}让每一台设备都值得信赖",
            "caption": "服务100+企业 | 品质认证",
        })

        # CTA
        storyboard.append({
            "shot": 5, "duration": f"{structure.get('cta', 5)}s",
            "visual": "品牌尾板+Logo+联系方式",
            "audio": outro_line.format(phone="XXX-XXXX", product_type=brand_name),
            "caption": outro_line.format(phone="XXX-XXXX", product_type=brand_name),
        })

        titles = [
            {"type": "痛点型", "text": f"还在为设备精度发愁？这家工厂的{brand_name}让人放心"},
            {"type": "反常识型", "text": f"一台{brand_name}的诞生过程，看完就懂了什么叫品质"},
            {"type": "身份认同型", "text": f"做制造业的都懂，{brand_name}这个参数意味着什么"},
        ]

        return {
            "titles": titles,
            "hook": {
                "type": "痛点解决",
                "visual": storyboard[0]["visual"],
                "audio": storyboard[0]["audio"],
                "text": storyboard[0]["caption"],
                "duration_s": structure.get("hook", 3),
            },
            "storyboard": storyboard,
            "bgm": {
                "style": "科技感电子 / 企业宣传大气",
                "bpm": "110-130",
                "recommendations": ["Inspiring Innovation", "Corporate Technology", "Future Factory"],
                "search_keywords": ["企业宣传", "科技", "工业", "大气", "电子"],
            },
            "post_production": {
                "editing": {"pace": "中速偏快", "transitions": "平滑溶解+硬切", "key_moments": "0s钩子, 3s产品特写, 18s参数叠加, 25s客户案例, 32s结尾CTA"},
                "color_grading": {"style": "冷色调工业风+提亮产品区域", "parameters": "对比度+10, 饱和度+5, 色温偏蓝"},
                "captions": {"font": "Noto Sans SC Bold", "style": "白字黑描边", "animation": "逐字弹出"},
                "sound_design": {"sfx": "参数出现时加科技感提示音", "audio_mixing": "人声-6dB, BGM-18dB, 音效-12dB"},
            },
            "tags": {
                "core": ["源头工厂", "品质制造", brand_name],
                "trending": ["自动化设备", "中国制造"],
                "long_tail": [f"{brand_name}工厂", "自动化生产线"],
            },
            "voiceover": self._voiceover_config(config),
        }

    def _extract_top_findings(self, report: dict) -> list:
        """Extract diverse findings across images, not just top-scoring globally.

        Strategy: pick top 2-3 findings from each image, prioritizing different
        detector types. This prevents a single image with many findings (e.g.
        85 text garbled items) from monopolizing all storyboard shots.
        """
        results = report.get("results", [report])
        diverse = []
        seen_imgs = set()

        for r in results:
            img = r.get("image", "")
            img_findings = []
            for d in r.get("detector_results", []):
                for f in d.get("findings", []):
                    f = dict(f)  # don't mutate original
                    f["detector"] = d["detector"]
                    f["_image"] = img
                    img_findings.append(f)

            # Sort this image's findings by score
            img_findings.sort(key=lambda x: x.get("score", 0), reverse=True)

            # Pick top findings from this image, favoring diversity:
            # take up to 3, but skip duplicates of same detector if already have enough
            picked_detectors = {}
            for f in img_findings:
                det = f["detector"]
                if det not in picked_detectors:
                    picked_detectors[det] = 0
                if picked_detectors[det] < 2:  # max 2 per detector per image
                    diverse.append(f)
                    picked_detectors[det] += 1
                if len([x for x in diverse if x.get("_image") == img]) >= 4:
                    break

        # Sort final list by score
        diverse.sort(key=lambda x: x.get("score", 0), reverse=True)
        return diverse

    def _voiceover_config(self, config: dict) -> dict:
        voice = config.get("voice", {})
        return {
            "method": voice.get("engine", "edge-tts"),
            "recommended_voice": voice.get("voice", "zh-CN-YunxiNeural"),
            "speed": str(voice.get("speed", 1.0)),
            "how_to_clone": "使用edge-tts命令行工具生成",
            "tips": "语速适中，每句之间留0.3s间隙方便后期剪辑",
        }

    def _post_process(self, script: dict, config: dict, brand: Optional[dict]) -> dict:
        """Fill missing fields from config defaults."""
        # Ensure voiceover config exists
        if "voiceover" not in script:
            script["voiceover"] = self._voiceover_config(config)

        # Fill missing storyboard durations
        for shot in script.get("storyboard", []):
            if not shot.get("duration"):
                shot["duration"] = "5s"

        # Merge brand tags
        if brand and brand.get("output", {}).get("hashtags"):
            existing_core = set(script.get("tags", {}).get("core", []))
            brand_tags = set(brand["output"]["hashtags"])
            script.setdefault("tags", {})
            script["tags"]["core"] = list(existing_core | brand_tags)[:5]

        return script


# ─── Convenience ──────────────────────────────────────────

def load_analysis_report(json_path: str) -> dict:
    """Load an analysis report JSON file."""
    with open(json_path, encoding="utf-8") as f:
        return json.load(f)
