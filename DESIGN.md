# DESIGN.md: Audience, Intent, and User Testing Notes

## 1. Audience Definition & Intent

### Intended Audience
* **Primary**: Ethiopian diaspora families, younger generation Ethiopians at home and abroad, and family members who cherish traditional cultural gatherings.
* **Viewing Context**: Mobile social feeds (Instagram Reels, TikTok, YouTube Shorts in 9:16) and family sharing platforms (WhatsApp, Telegram, widescreen family screens in 16:9).
* **Target Emotional State**:
  * Deep nostalgic warmth (*Tizita*).
  * Pride in Ethiopian hospitality, culinary heritage, and elder respect.
  * A sense of rootedness: remembering that family unity is what makes life meaningful.

### One-Sentence Intent Statement
> *"To evoke a profound sense of cultural belonging and gratitude in Ethiopian viewers by transforming everyday family traditions—breaking injera together, receiving a grandmother's gursha, and sharing coffee—into an enduring cinematic memory."*

---

## 2. Stated Reason for Every Shot

Every shot in `storyboard.json` exists for a concrete narrative, emotional, or pacing reason:

| Shot ID | Scene Title | Stated Narrative & Emotional Reason |
| :---: | :--- | :--- |
| **shot_01** | The Hearth of Memories | **Establishes Sanctuary**: Grounds the viewer in the quiet, peaceful dawn of an authentic home before anyone speaks, signaling peace and nostalgia. |
| **shot_02** | The Hands of Tradition | **Honors Unseen Labor**: Focuses on the grandmother's weathered hands making injera, connecting cultural continuity directly to mothers' dedication. |
| **shot_03** | When Family Comes Together | **Injects Energy & Warmth**: Breaks the early morning quiet with dynamic physical embraces and arrival of relatives, showing family as an active reunion. |
| **shot_04** | Preparing the Shared Feast | **Visual Celebration of Heritage**: Overhead geometric showcase of Ethiopian cuisine (Mesob, Doro Wat, Alicha), highlighting collective teamwork before eating. |
| **shot_05** | One Mesob, Many Generations | **Thematic Core & Climax 1**: The visual centerpiece where elders and children sit shoulder-to-shoulder, translating "unity" from an abstract word into a shared physical act. |
| **shot_06** | The Gursha of Blessing | **Emotional Heart**: The peak intimate beat of the film. A grandmother feeding her grandson communicates affection more powerfully than any dialogue can. |
| **shot_07** | The Sacred Coffee Ceremony | **Pacing Shift to Contemplation**: Slows down the film after eating. Smoke, clay jebena, and glowing coals provide sensory depth and room to breathe. |
| **shot_08** | Stories Passed Between Generations | **Transmission of Wisdom**: Connects oral history to the youth. Grandfather speaking and grandson listening cements the intergenerational bridge. |
| **shot_09** | What Remains Across Time | **Philosophical Resolution**: Wide golden hour tableau pulling back into the landscape, reinforcing that while years pass, cultural love endures. |
| **shot_10** | Heritage End Card & AI Disclosure | **Honesty & Attribution**: Displays film title, emotional tagline, and transparent AI attribution without abrupt cut-off. |

---

## 3. User Testing Records

### User Test 1: The Radio Cut (Prototype Checkpoint)
* **Date**: November 2026
* **Format**: Audio animatic (Amharic narration over placeholder Tizita acoustic krar score on a black screen with timestamps).
* **Participants**:
  1. *Participant A* (Ethiopian diaspora university student, 22): Listened on phone headphones.
  2. *Participant B* (Mother & homemaker, Addis Ababa, 48): Listened on phone speaker.
  3. *Participant C* (Family elder, 67): Listened in quiet living room.

#### Feedback & Findings
* **Pacing**:
  * *Feedback*: Participant A noted that Shot 05 (the Mesob scene) felt too brief in an early 7-second draft because listeners wanted to absorb the fullness of the family gathering.
  * *Change Made*: Extended Shot 05 to **11.0 seconds** and expanded Shot 07 (Coffee ceremony) to **11.0 seconds** to allow natural pauses between speech.
* **Amharic Voice Clarity & Tone**:
  * *Feedback*: Participant B remarked that the tone should sound like a family member speaking from the heart, not an official radio news broadcaster.
  * *Change Made*: Updated TTS steering prompt to `warm, contemplative, slow, deeply heartfelt, unhurried`.
* **Cultural Resonance**:
  * *Feedback*: Participant C smiled during the Gursha line, commenting: *"That is the exact moment when you feel you are loved."*

---

### User Test 2: The Near-Final Composite Edit
* **Date**: 2026-11-25
* **Artifact Tested**: `outputs/final/film_16x9.mp4` and `outputs/final/film_9x16.mp4` (Full 90.00s films with burned-in bilingual subtitles, ducked score, and AI disclosure end card).
* **Participants**:
  * **Participant A** (Native Amharic speaker, family historian): Evaluated cultural authenticity, Ge'ez subtitle typography, and emotional resonance.
  * **Participant B** (Non-Amharic speaker): Evaluated English subtitle readability, narrative pacing, and emotional connection.
  * **Participant C** (Video producer): Evaluated broadcast loudness (-14 LUFS), sidechain ducking smoothness, and 9:16 mobile safe-zone margins.
* **Findings & Feedback**:
  1. *Subtitle Legibility*: Both participants praised the stacked two-line format (Amharic white 42pt top, English light-gray 32pt bottom with black outline). The mobile safe-zone offset in 9:16 (`MarginV=330`) prevents TikTok/Reels UI icons from obstructing text.
  2. *Audio Balance*: Voice remains perfectly intelligible over the traditional Krar and Washint score. The -14 dB sidechain ducking with 150ms attack and 900ms release avoids volume "pumping".
  3. *AI Disclosure*: The 7-second end card was found respectful, clearly crediting the family heritage while transparently disclosing the multi-model pipeline.
* **Verdict**: **Approved for Final Release** ✅

