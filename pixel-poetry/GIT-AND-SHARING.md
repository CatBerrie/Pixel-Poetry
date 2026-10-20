# 🌸 Pixel Poetry: open it, push it, share it

## 1) Open it in VS Code (Mac)
1. Unzip `pixel-poetry-site.zip` (double-click it). You get a folder called `pixel-poetry`.
2. VS Code → **File → Open Folder…** → choose `pixel-poetry`.
3. Install the **Live Server** extension (Extensions icon, search "Live Server", Install).
4. Right-click `index.html` → **Open with Live Server**. The site opens in your browser, and downloads work with one click.

## 2) Put it on GitHub (first time only)
In VS Code press **Ctrl + `** to open the Terminal, then run:

```bash
git --version                      # if it asks to install developer tools, click Install
git config --global user.name  "Arpita Firoz"
git config --global user.email "arpitafiroz0@gmail.com"

git init
git add .
git commit -m "First version of Pixel Poetry"
git branch -M main
```

Now create an empty repo: github.com → **+** → **New repository** → name it `pixel-poetry` → Public → **Create** (don't tick README).
GitHub then shows you a URL. Connect and push:

```bash
git remote add origin https://github.com/YOUR-USERNAME/pixel-poetry.git
git push -u origin main
```

GitHub does not accept your password. When asked to sign in, VS Code opens the browser. Click **Authorize** and it works.
(Your `originals/` folder is ignored by `.gitignore`, so your full-quality photos never go online.)

## 3) Get a link anyone can open (free)
GitHub repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch: **main** / **(root)** → **Save**.
After about a minute your site is live at:

`https://YOUR-USERNAME.github.io/pixel-poetry/`

Send that link to friends. Everything works there (hover, lightbox, search, one-click download).

## 4) Update it later (every time you change something)
```bash
git add .
git commit -m "Added 5 new photos"
git push
```
The live site updates in about a minute. In VS Code you can click the **Source Control** icon (left bar), type a message, click **Commit**, then **Sync Changes**.

Mark a "version" like a release:
```bash
git tag v1.1 -m "New nightfall section"
git push --tags
```

## 5) Adding new photos
1. Put the originals in `originals/`
2. Run `python3 make_photos.py`
3. Paste the printed lines into the `photos` list in `index.html`
4. Commit + push (step 4)

## 6) Collecting reviews
- Easy: make a **Google Form** ("What did you think?"), copy its link, paste it into `feedbackUrl:""` near the top of the script in `index.html`. A "💌 Feedback" button appears in the top bar.
- Later (Level 3): likes and comments shared by everyone need a small database (Firebase). Right now likes and views are saved only in each visitor's own browser.
