# 🌿 Pixel Poetry

Your nature photography website.

## Open it
- **Quick look:** double-click `index.html`.
- **Best way (one-click downloads):** open this folder in VS Code → right-click `index.html` → **Open with Live Server**.
  (Or in a terminal inside this folder: `python3 -m http.server 8000`, then visit http://localhost:8000)

## What's inside
- `index.html`  the whole website (HTML + CSS + JavaScript). Sections are labeled A, B, C... in the code.
- `photos/`  the pictures people see. `photos/download/` holds the watermarked copies for the Download button.
- `originals/`  put your full-size photos here (this folder is ignored by Git).
- `make_photos.py`  makes the web + watermarked copies and the color chips for any new photo.

## Add a new photo
1. Drop the original into `originals/`
2. Run `pip3 install pillow` (once), then `python3 make_photos.py`
3. Paste the line it prints into the `photos` list in `index.html` and write your title + caption.

---

## 🌍 Put it online (GitHub Pages) + update it later

First time (Terminal inside VS Code: Terminal → New Terminal):

```bash
git init
git add .
git commit -m "Pixel Poetry first version"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/pixel-poetry.git
git push -u origin main
```

Then on github.com: repo → Settings → Pages → Source: "Deploy from a branch" → Branch: main / (root) → Save.
After ~1 minute your link is `https://YOUR-USERNAME.github.io/pixel-poetry/`

Every time you change something:

```bash
git add .
git commit -m "what I changed"
git push
```

(`originals/` is in .gitignore on purpose, so your un-watermarked photos never get uploaded.)
