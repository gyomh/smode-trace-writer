# Smode Trace Writer

*[Version française](README.fr.md)*

> **Experimental, not an official Smode tool.** Built by trial and error against the Oil API (see [smode-oil-reference](https://github.com/gyomh/smode-oil-reference)). Tested on Smode Compose R15.

A reusable Script that **paints a line from the position of a moving point**: it reads the X / Y position of a
ShapeLayer and writes the Y value into the control point of a path (`PathShapeGenerator`) at the matching X index.
It interpolates between the previous and the new index so there are **never holes at high speed**. Developed for
[smode-oscilloscope](https://github.com/gyomh/smode-oscilloscope).

## Install

1. Drag `trace_writer.py` into your Smode project, **Launch Mode = At Every Update** (mandatory: it reads a position
   continuously).
2. **Quick test:** leave `movingShape` and `lineShape` empty and execute: a complete demo (point + line + linear loop
   on X, sine on Y) is created and wired.
3. **Your own shapes:** drag them into `movingShape` and `lineShape` **before the first run** (the demo is only built
   when both are empty). `nPoints` is only used for the demo line.

## License

MIT — see [LICENSE](LICENSE).
