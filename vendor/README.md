# Vendor — steal physics, not identity

Cloned **as reference**. Do not run as Monarch. Lift modules → rewrite into `monarch/`.

## Cloned here

| Repo | Why it maps to us | Steal | Kill |
| --- | --- | --- | --- |
| [Stickman-Studio](https://github.com/saiedpod-bot/Stickman-Studio) | Closest product: script → stickman stills/Veo → TTS → ffmpeg → YT | scene storyboard, Ken Burns slideshow cheap path, TTS, ducking BGM | their Gemini-only brain, auto-publish public, $0 slideshow as the *look* |
| [faceless-youtube-agents](https://github.com/yashaiguy-dev/faceless-youtube-agents) | **Viral DNA**: scrape top videos, transcribe, extract hooks/rhythm | channel clone loop, DNA extract, pipeline stages | Gathos lock-in, “clone any channel” as the product (we elevate 5x, not impersonate) |
| [Viral-Faceless-Shorts-Generator](https://github.com/Dark2C/Viral-Faceless-Shorts-Generator) | Trends → script **approve gate** → Piper TTS → align → FFmpeg | human approve before render (our HAAN), Piper local TTS, Aeneas timing | gameplay background as default, Google Trends as only hunt |
| [AI-Youtube-Shorts-Generator](https://github.com/SaarD00/AI-Youtube-Shorts-Generator) | Hook→context→mechanism→twist scripts, edge-tts, ffmpeg xfade | script spine, silence trim, composer | Pexels b-roll as hero (we are stickman), random avatar insert |

## Do not clone whole (use as lib / later)

| Repo | Job |
| --- | --- |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | transcripts + competitor download |
| [youtube-transcript-api](https://github.com/jdepoorter/youtube-transcript-api) | captions without full video |
| [edge-tts](https://github.com/rany2/edge-tts) | free neural VO |
| [Piper](https://github.com/rhasspy/piper) | local VO |
| [MoviePy](https://github.com/Zulko/moviepy) | compose |
| [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | word timing for captions |
| [Remotion](https://github.com/remotion-dev/remotion) | later: programmatic stickman in React if we leave Flow |
| [claude-code-video-toolkit](https://github.com/digitalsamba/claude-code-video-toolkit) | explainer-short template, karaoke captions |
| [awesome-faceless](https://github.com/sasharun/awesome-faceless) | tool map, not code |
| [openshorts](https://github.com/mutonby/openshorts) | clip/title/thumb SaaS — too heavy, wrong core (talking heads) |
| [claude-youtube](https://github.com/AgriciDaniel/claude-youtube) | skill surface: audit/script/seo/thumb — steal command map, not Claude lock-in |

## Map onto Monarch states

- Hunt/forensic ← faceless-youtube-agents + yt-dlp
- Ideas/script ← Shorts generator spine + our constitution
- Character/prompts ← Stickman-Studio + our MONARCH_ENGINE
- VO/timing ← edge-tts / Piper / ElevenLabs + Aeneas/whisper
- Edit/SFX ← ffmpeg/moviepy from Viral-Faceless + our grammar
- HAAN ← their approve-script gate

Upload is **human**. Do not clone upload-only factories as runtime.
