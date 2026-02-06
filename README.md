## Run-O-Matic.

Devel branch of new gen Run-O-Matic

The main functionality of this app used X11 capabilities to embed an application inside a target window.
Wayland works in a total different way so the code should be rewritten from scratch.

### 1. Design

- Run-O-Matic was desktop agnostic and only dependand on QT and X11. This new release will be Plasma focused
- A KWin plugin will launch all apps in FullScreen mode
- Run-O-Matic will be a launcher module, like kickoff, in dashboard mode
- All shortcuts will be inhibited

