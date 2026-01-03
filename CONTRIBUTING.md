# Contributing to The Ark 🚢

**Welcome, Builder.** You are adding to the repository of human sovereignty.

This guide is designed to get you from "Idea" to "Merged" as fast as possible, especially if you are adding a **Mini-Game** or **Module**.

## 🚀 Quick Start

1. **Clone the Repo**:

    ```bash
    git clone https://github.com/seekerflame/theArk.git
    cd theArk
    ```

2. **Create Your Branch**:

    ```bash
    git checkout -b feature/my-cool-game
    ```

## 🎮 Adding a Game/Module

We love games. They are the best way to teach abundance.

1. **Where to put it**:
    Go to `web/modules/` and create a folder for your game:

    ```bash
    mkdir web/modules/space_invaders
    ```

2. **Files you need**:
    * `index.html` (or just your JS file if it's dynamic)
    * `game.js` (Your logic)
    * `style.css` (Your style)

3. **Hooking it up**:
    Open `web/index.html` and look for the Modules section. Add a button or link to your game.
    *Ideally, ask the Lead Architect (Antigravity) to help verify where it fits in the navigation.*

## 🛠 Tech Stack & Rules

* **Vanilla is King**: We prefer raw HTML/CSS/JS. No heavy frameworks (React/Vue/Angular) unless absolutely necessary.
* **Offline First**: Assume the internet is down. Does your game still work?
* **Assets**: Put images/sounds in `web/assets/`.

## 🤝 Submitting

1. **Commit your changes**:

    ```bash
    git add .
    git commit -m "[NEW] Added Space Invaders prototype"
    ```

2. **Push**:

    ```bash
    git push origin feature/my-cool-game
    ```

3. **Open a Pull Request** on GitHub and tag `@seekerflame`.

---
**"We do not ask for a better world. We build it."**
