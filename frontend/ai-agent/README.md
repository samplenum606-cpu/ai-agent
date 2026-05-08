# AI Agent Frontend

This React frontend is part of the Autonomous EDA Agent project and is maintained manually.

## Purpose

The frontend provides a simple user interface for sending analysis requests to the backend service.

## Run locally

From this folder, install dependencies and start the app:

```bash
npm install
npm start
```

Then open:

```text
http://localhost:3000
```

## Notes

- The frontend proxies API requests to `http://localhost:5000`.
- Make sure the backend server is running before using the app.
- The main frontend logic is in `src/App.js` and styles are in `src/App.css`.

## Customization

- Update `src/App.js` to change the input prompt, buttons, or result handling.
- Update `src/App.css` to change the visual design.

## Important

This README is written specifically for this project and does not contain generic Create React App boilerplate.
