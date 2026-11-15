# Design Decisions & Revision Log: IKEA TISKEN Soap Drainer

## `v001` — Initial Round Slotted Dish
- **Changes**: `Ø110 mm` round cup (`16 mm` tall, `3.5 mm` wall), parallel floor slots, `4 mm` raised ribs, `32 mm` wide hook (`8.5 mm` throat).
- **User Feedback**: Requested minimalist style that drips directly into the bath.

## `v002` — Minimalist Forward Waterfall Spout
- **Changes**: Lowered rim to `13 mm`, `2.4 mm` wall, `3.5°` forward sloped floor with `36 mm` front waterfall spout lip, slimmed hook to `22 mm` (`~20.9 g`).
- **User Feedback**: "you can make the bottom hollow".

## `v003` — Hollow-Bottom Parallel Slats
- **Changes**: Removed solid floor completely (`11 mm` ring + 5x `2.4 mm` open slats, `13.6 mm` air gaps), `~10.9 g`.
- **User Feedback**: "make it look nicer, japanese style, minimalist".

## `v004` — Japanese Minimalist (*Hamon* Zen Ripple Edition) [Current]
- **Changes**:
  - Replaced plain cylinder wall with chamfered bowl-style outer ring (`Ø110 mm × 10.5 mm`, `1.1 mm` top/bottom bevels).
  - Replaced straight slats with concentric *Hamon* water-ripple rings (`Ø64 mm` & `Ø24 mm`) joined by 6 radial `2.2 mm` spokes (~82% open hollow bottom).
  - Slimmed hook to `18 mm` with chamfered top corners while preserving the `8.5 mm` TISKEN rail throat.
- **Geometry Checks**: Verified via `scripts/cad_check.py` (`17.6 cm³`, `~9.8 g` PETG, `0` overhangs >45°? — see `exports/v004/manifest.json`).
