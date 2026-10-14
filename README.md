# Tool Battle Music 1.5.1

Remove exact leading PCM silence from 107 generation-specific tracks. Preserve audible samples, quiet introductions, volume and all pauses after the music begins. Future renders trim the silent pickup automatically.

Audio packs are now 1.0.1. Open OPTIONS > TOOL MUSIC > DOWNLOAD ASSETS to update the pack for your current generation. The previous packs remain available; updated packs include pinned file hashes. Shuffle history and curated area assignments are retained.

Testing skipped at the user's request.

# Tool Battle Music 1.5.0

Add OUTSIDE BATTLE: Area Defaults (default), Random, or Original. Area Defaults assigns one fixed thematic song to each of 3,947 extracted maps across all eleven games, including buildings, caves and post-game areas. See AREAS.md for every assignment. Original preserves native field music.

All Random battle categories and outside-battle Random share one saved shuffle pool. Each new battle or area draws an unused song; the pool refills after all available songs have been played and avoids an immediate repeat at the cycle boundary. Fixed/curated choices also mark their songs played in that pool, but deliberately selected fixed songs can repeat. Repeated engine cues within a battle or area retain the same selection. The pool is stored in persistent mod cache and save data; settings changes and battles do not reset its history.

Reuse the existing generation-specific audio packs and in-game downloader. No new audio download is required. Native fanfares, victory music, fades and pause/ducking remain controlled by the engine.

Testing skipped at the user's request. Restart after updating, then open OPTIONS > TOOL MUSIC > OUTSIDE BATTLE.

# Tool Battle Music 1.4.0

For gen1recomp 0.3.54 or newer (before 0.4.0). One ZIP supports Red/Blue/Yellow,
Gold/Silver/Crystal, and Ruby/Sapphire/Emerald/FireRed/LeafGreen. The active game
automatically selects its music engine adapter, soundtrack, and settings UI.
Gen 1 uses the classic renders; Gen 2 uses the four-voice renders; Gen 3 uses
the stereo PCM-style renders. No generation selection is needed.
Import the release ZIP through the launcher mod manager and enable the mod.
Allow its network and engine-code permissions. Open **OPTIONS > TOOL MUSIC >
DOWNLOAD ASSETS** and press A to download the audio pack for the current game's
generation. The screen shows download and installation progress; B cancels a
transfer or returns to settings. No custom audio is played until it is available;
vanilla battle themes remain usable while assets are missing.

The small core ZIP contains the mod and settings. Three independently cached
audio packs live on GitHub Releases: Gen 1 (~405 MB), Gen 2 (~461 MB), and Gen 3
(~1.06 GB). Each file is checked against a pinned SHA-256 catalog before installation.
The asset screen can also remove the downloaded pack and download it again.
Existing bundled audio remains supported and can be migrated locally into cache.
Open OPTIONS > TOOL MUSIC, or MODS > the Tool Battle Music entry > OPTIONS,
to select regular battle, Gym Leader,
and Pokemon League music independently. Each offers 41 songs, Original, and Random.
Regular covers wild and ordinary trainer battles. League covers the Elite Four
and Champion (also Red in Gen 2). Gym leaders have their own setting.
Random picks once per battle and avoids repeating the previous random song in that
category. Victory jingles and overworld themes retain their existing behavior.

The original ten songs come from https://www.midiworld.com/files/1117/ .
31 additional songs come from https://midifind.com/files/t/tool/1822-1-10 .
See SONGS.md for the complete list and direct source links. Alternate arrangements,
title aliases, and overlapping medleys are omitted. MIDI hashes and musical-event
fingerprints were checked to prevent duplicate imports. Compositions by Tool (and
the respective composers of cover songs);
MIDI arrangements belong to their respective creators. No affiliation is implied.
Original MIDI files are in `midi/`; `audio/` holds full-length synthesized chip-style
FLAC renders because the engine cannot stream MIDI directly. Gen 2 uses two pulse
voices, a 16-step bass wave voice, and one percussion voice, with four simultaneous
voices and quantized note volume. Gen 3 uses 32 kHz stereo, PCM-style instrument
timbres selected from MIDI programs, stereo positioning, and full MIDI polyphony.
These are custom chip-style arrangements, not cycle-accurate emulations or native
ROM music bytecode. No original recordings
or soundfonts are included. The soundtrack loops at the end of each song.

Rebuild: install Python packages numpy, mido, and soundfile, then run
`python tools/render.py --style gen2` or `--style gen3`. Downloads are optional
with `--download`. Engine code permission is required for the generation-specific
audio adapters. Import ToolBattleMusic-v1.4.0.zip to upgrade the original mod.
Disable the separate Tool Battle Music Gen 2 / Gen 3 variants before enabling
this unified mod. Public repository: https://github.com/Bentley734/ToolBattleMusic .
The audio downloader is adapted from the 1025Dex/KIM asset manager, including its
native Gen 3 UI and portable-mode download handling. See CREDITS.md.
