# Tool Battle Music 1.6.0

Add 49 distinct full arrangements: TOOL - Fear Inoculum; 12 Pink Floyd, 10 Rush, 10 A Perfect Circle, 8 Rage Against the Machine and 8 Puscifer songs. Total library: 90 songs. Separate optional packs for each artist and generation; TOOL EXTRAS contains Fear Inoculum without requiring another download of the original TOOL pack.

ARTIST MIX defaults to TOOL ONLY. ALL INSTALLED enables downloaded optional artists for Random and Area Defaults. Download any combination using the separate GET artist rows. Mixed curated defaults cover every supported area with ordered fitting choices; missing optional packs fall back to an installed choice or the original TOOL assignment. See MIXED-AREAS.md for all assignments and EXPANSION-SONGS.md for sources.

The shared saved shuffle tracks played songs across battles and locations. Newly installed artists join the unused pool; changing artist mode preserves played history. TOOL ONLY skips optional artists in battle song selectors and automatic playback. Original remains available.

Every new render begins at its first nonzero PCM sample; audible intros and internal pauses are preserved. Reuse the existing trimmed TOOL 1.0.1 packs. Existing saved choices and shuffle state remain compatible.

Free alternative arrangements were used as requested: MIDIfind and Songparts. Supreme MIDI requires a subscription and restricts its files to private use; RushMIDI's certificate failed validation. Duplicate song variants and a short Puscifer fragment were omitted. No original audio recordings or soundfonts are distributed.

Testing skipped at the user's request. Restart after updating; open OPTIONS > TOOL MUSIC, download desired packs, then choose ARTIST MIX > ALL INSTALLED.

# Tool Battle Music 1.5.1

Remove exact leading PCM silence from 107 generation-specific tracks. Preserve audible samples, quiet introductions, volume and all pauses after the music begins. Future renders trim the silent pickup automatically.

Audio packs are now 1.0.1. Open OPTIONS > TOOL MUSIC > DOWNLOAD ASSETS to update the pack for your current generation. The previous packs remain available; updated packs include pinned file hashes. Shuffle history and curated area assignments are retained.

Testing skipped at the user's request.

# Tool Battle Music 1.5.0

Add OUTSIDE BATTLE: Area Defaults (default), Random, or Original. Area Defaults assigns one fixed thematic song to each of 3,947 extracted maps across all eleven games, including buildings, caves and post-game areas. See AREAS.md for every assignment. Original preserves native field music.

All Random battle categories and outside-battle Random share one saved shuffle pool. Each new battle or area draws an unused song; the pool refills after all available songs have been played and avoids an immediate repeat at the cycle boundary. Fixed/curated choices also mark their songs played in that pool, but deliberately selected fixed songs can repeat. Repeated engine cues within a battle or area retain the same selection. The pool is stored in persistent mod cache and save data; settings changes and battles do not reset its history.

Reuse the existing generation-specific audio packs and in-game downloader. No new audio download is required. Native fanfares, victory music, fades and pause/ducking remain controlled by the engine.

Testing skipped at the user's request. Restart after updating, then open OPTIONS > TOOL MUSIC > OUTSIDE BATTLE.

Tool Battle Music 1.4.0 — in-game asset downloads

- Small core mod plus three audio packs, automatically chosen by game generation.
- OPTIONS > TOOL MUSIC > DOWNLOAD ASSETS opens the same style of asset manager
  used by KIM1025/1025Dex, with download/install progress, cancel/retry and cache removal.
- Pinned per-file SHA-256 verification rejects wrong, modified or unsafe packs.
- Vanilla themes remain playable when assets are absent; downloaded tracks work
  immediately, including portable cache installations.
- Network permission added; 41 songs, all existing settings and matched volume retained.
- Validated 343 downloader UI assertions, installation/checksum/path/disk-full
  cases, portable-safe audio resolution and existing all-eleven-game music tests.

- Added 31 unique songs from MIDIfind, for 41 total. One arrangement per song;
  alternate versions, spelling aliases and overlapping medleys excluded.
- New songs rendered for all three generations with the established loudness target.
- Catalog, source links and import fingerprint checks included.

- Raised quieter soundtrack renders to 0.17 RMS, using measured vanilla GBA
  battle themes (0.1455–0.1706 RMS) as the reference. Louder renders retain their level.
- Soft peak limiting preserves headroom; native music volume and mute controls remain active.

- Fixed Emerald compatibility and added OPTIONS > TOOL MUSIC plus a static MODS schema.
- One package automatically selects Gen 1, Gen 2 or Gen 3 audio assets, engine
  adapters and settings menus for all eleven supported games.
- Declared conflicts prevent enabling the separate Gen 2/Gen 3 variants alongside it.
- Gen 2 has four-voice arrangements, including separate Elite Four/Champion/Red routing.
- Gen 3 has stereo PCM-style arrangements, native BGM volume/pause integration,
  and distinct FR/LG League routing despite Elite Four sharing the gym music.
- Complete chip-style renders of all 41 MIDI arrangements from MIDIWorld and MIDIfind.
- Independent song, Random, and Original settings for regular battles, Gym Leaders,
  and the Pokemon League (Elite Four plus Champion).
- Stable random choice throughout each battle; consecutive random repeats avoided.
- Original MIDI sources and reproducible render tools included.
- Validated manifest and music definitions against gen1recomp 0.3.54 engine schemas.
- Automated routing checks cover all five League opponents, Giovanni's gym and
  ordinary encounters, original themes, overworld and victory passthrough, and
  2,000 randomized battles including repeated transition cues and all 41 choices.
- All 123 audio files decoded and checked for duration, loudness, peaks, and finite samples.

Import ToolBattleMusic-v1.4.0.zip through the launcher mod manager and disable
the separate generation variants. Supports Red/Blue/Yellow, Gold/Silver/Crystal,
and Ruby/Sapphire/Emerald/FireRed/LeafGreen automatically.
Audio renders use a custom chip-style synthesis,
not original recordings. Live in-game listening has not been verified.
Download the active generation's audio through OPTIONS > TOOL MUSIC > DOWNLOAD ASSETS.
