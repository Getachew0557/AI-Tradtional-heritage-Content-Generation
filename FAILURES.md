# FAILURES.md: Blocker & Troubleshooting Journal

This journal documents real obstacles encountered during pipeline development, the diagnostics conducted, and the verified solutions implemented.

---

### Failure 01: Legacy Gemini Model Deprecation (HTTP 404)
* **What Broke**: Calling `gemini-2.0-flash` or `gemini-2.5-flash-lite` in the Gemini API returned `404 NOT_FOUND: This model is no longer available`.
* **Root Cause**: Google AI Studio retired older flash previews in favor of the active Gemini 3 family.
* **What We Tried**:
  1. Testing `gemini-2.5-flash` (encountered transient 503 high-demand spike).
  2. Querying `client.models.list()` dynamically.
* **Resolution**: Successfully targeted active `gemini-3.5-flash-lite` and `gemini-3-flash-preview`. Documented model fallback cascade in code.

---

### Failure 02: Cloudflare API Token Email Verification Block
* **What Broke**: Attempting to generate a Cloudflare Workers AI token returned an ambiguous popup: *"An unknown error occurred. Please verify your email."*
* **Root Cause**: Cloudflare security policy restricts API token provisioning until the registered account email is validated.
* **What We Tried**: Inspected browser UI alerts and Gmail inbox.
* **Resolution**: Located the verification email in Gmail, confirmed account email, and regenerated token with `Workers AI: Read/Edit` permissions. Tested with HTTP 200 response on `@cf/black-forest-labs/flux-1-schnell`.

---

### Failure 03: Kaggle API New Token Format (`KGAT_`) Handling
* **What Broke**: Direct HTTP basic auth with Kaggle's newly introduced `KGAT_` token prefix returned HTTP 404 on legacy endpoints.
* **Root Cause**: Kaggle updated their authentication protocol from legacy `kaggle.json` (`username` + `hex_key`) to a unified `KAGGLE_API_TOKEN` (`KGAT_...`) read via `~/.kaggle/access_token` by the official Kaggle SDK.
* **What We Tried**: Installed official `kaggle` package into `agentic_env` and wrote `~/.kaggle/access_token`.
* **Resolution**: Official `KaggleApi().authenticate()` successfully validated the token without errors.

---

### Failure 04: Windows FFmpeg Executable Resolution
* **What Broke**: Calling `ffmpeg` in standard Windows PowerShell returned `ObjectNotFound: The term 'ffmpeg' is not recognized`.
* **Root Cause**: The user's system did not have global administrative PATH access for native ffmpeg installation.
* **What We Tried**: Installed `imageio-ffmpeg` directly into the `agentic_env` virtual environment.
* **Resolution**: Built `pipeline/utils/ffmpeg_helper.py` which dynamically discovers either system `ffmpeg` or `imageio_ffmpeg.get_ffmpeg_exe()`, providing a seamless broadcast-grade FFmpeg 9.0.2 executable without requiring admin rights.
