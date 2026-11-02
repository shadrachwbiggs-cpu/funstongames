# Funston Games website

The website for Funston Games and its games, starting with Rally the Realm.

- `pages/` holds each page's own text. `pages/rally-the-realm/` is the Rally the Realm section; a future game gets its own folder beside it.
- `static/` holds the stylesheets and images.
- `site.json` holds the company name, contact email, web address, and the App Store link. When Rally the Realm is on the App Store, put its link in `rallyTheRealm.appStoreUrl` and every "Coming soon" sign becomes a download button.
- `python3 build.py` builds the finished site into `docs/`, which GitHub Pages serves. Never edit `docs/` by hand.
- Preview locally: `python3 -m http.server 8642 -d docs`, then open http://localhost:8642.
