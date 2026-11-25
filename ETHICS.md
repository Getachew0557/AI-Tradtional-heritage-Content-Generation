# ETHICS.md: Likeness Consent, Model Licenses, and Labeling Plan

## 1. Consent Record for Likeness and Voice

### Ethical Foundation
This film, *"The Memories of Our Home"*, is dedicated to Ethiopian family traditions and ancestral values. As required by the project ethics gate:
> *"If a real person's voice or face appears, we ask for their recorded, informed consent for this use, and that the words in their mouth are ones they agreed to."*

### Recorded Consent Registry

| Person / Role | Likeness Representation | Consent Status | Approved Scope |
| :--- | :--- | :---: | :--- |
| **Grandmother (Ayelech)** | Visual reference sheet `references/characters/grandmother_ref.jpg` depicting warm elder in white Netela. | **Consent Recorded & Verified** ✅ | Informed consent granted to use likeness as reference for AI image conditioning depicting grandmotherly blessing and Gursha. |
| **Grandfather (Tadesse)** | Visual reference sheet `references/characters/grandfather_ref.jpg` depicting elder in turban with white beard. | **Consent Recorded & Verified** ✅ | Informed consent granted for elder storytelling depiction. |
| **Mother (Marta)** | Visual reference sheet `references/characters/mother_ref.jpg` in Habesha Kemis. | **Consent Recorded & Verified** ✅ | Informed consent granted for culinary preparation representation. |
| **Grandson (Yonas)** | Visual reference sheet `references/characters/child_ref.jpg` in traditional tunic. | **Parental Consent Verified** ✅ | Parental guardian consent granted for depiction receiving family traditions and Gursha. |
| **Family Group References** | Cultural group dining and coffee ceremony photos (`references/style/`). | **Verified** ✅ | Used strictly for cultural clothing, mesob arrangement, and lighting style conditioning. |

*All words spoken in narration are non-defamatory, cultural proverbs and shared family wisdom agreed upon by family members.*

---

## 2. Model & Asset Licenses

| Tool / Model | Component | License Type | Terms & Commercial Use |
| :--- | :--- | :---: | :--- |
| **Google Gemini 3.8 Flash** | Script & Storyboard validation | Google AI Studio Terms of Service | Permitted for development, testing, and creative generation. |
| **Gemini 3.8 Flash TTS** | Amharic Narration speech synthesis | Google AI Studio Terms of Service | Permitted speech generation. |
| **FLUX.1 schnell** | Keyframe generation (Cloudflare) | Apache 2.0 | Open weights, commercial and personal use allowed. |
| **FLUX.2 klein (4B)** | Keyframe generation | Apache 2.0 | Open weights, permissive open use. |
| **Wan 2.2 TI2V-5B** | Image-to-Video motion generation | Apache 2.0 | Open weights, fully permissive commercial & academic use. |
| **ACE-Step 1.5** | Original Ethiopian music score | MIT License | Permissive open-source; outputs usable commercially. |
| **FFmpeg 9.0.2** | Compositing, ducking, mastering | LGPL v2.1+ / GPL | Free and open source software. |

---

## 3. Transparency & AI Content Labeling Plan

1. **In-Film Attribution (End Card)**:
   * Shot 10 includes a visible, legible 7-second end card:
     * *Title*: የቤታችን ትውስታ — The Memories of Our Home
     * *Tagline*: ባህላችን በእኛ ውስጥ ይኖራል። ("Our traditions live through us.")
     * *AI Disclosure*: *"AI-generated film. Created with AI-assisted pipeline orchestration (Gemini, FLUX, Wan 2.2, ACE-Step, FFmpeg)."*
2. **Platform Disclosure**:
   * When posted on YouTube, TikTok, or Instagram, the native platform switch **"Altered or synthetic content" / "AI-generated content"** is enabled.
3. **Provenance & Metadata Integrity**:
   * Output video MP4 files retain digital metadata and do not strip any synthetic media provenance markers.
