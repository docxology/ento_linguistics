# Preamble and document styling

The standalone renderer reads [preamble.tex](preamble.tex) directly. This Markdown file documents that source; it does not inject a second set of LaTeX commands.

Paper metadata comes from [config.yaml](config.yaml). The renderer generates the title-page include and PDF metadata during the build, then applies its citation/link postprocessing. Keep metadata in the configuration rather than duplicating it in a preamble example.

For figures, captions, equations, bibliography conventions, and strict rendering, use [the authoring guide](../guides/authoring.md). For external Pandoc/TeX prerequisites, use [setup](../guides/setup.md).

After changing preamble.tex, rebuild the paper and inspect pages, glyphs, references, and float placement. Guide and navigation edits alone do not change the rendered manuscript.
