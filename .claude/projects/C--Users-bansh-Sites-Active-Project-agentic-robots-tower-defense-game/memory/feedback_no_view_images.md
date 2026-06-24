---
name: Do not view generated images
description: Stop reading/viewing generated PNG files to save tokens -- let the user review and pick
type: feedback
---

Do not use the Read tool to view generated image files. Viewing images consumes too many tokens.

**Why:** User noticed excessive token consumption from viewing 10-20 images per batch.

**How to apply:** After generating images, tell the user the file paths and let them review locally. Only view an image if the user explicitly asks you to look at a specific one.
