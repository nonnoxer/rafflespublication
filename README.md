# Raffles Publications Site

## About

This project was started as a custom website created for the Raffles Publications Co-Curricular Activity in Raffles Institution. The goal was to create a fully customisable frontend with a simple cms and corresponding backend.

The backend was completed by @nonnoxer and the frontend will be completed by @ChenNuode.

## Brief Structure of Code

* All regularly viewable pages are rendered to the same jinja template ```templates/content.html```
* All posts, custom pages, users and feedback are stored in ```databases```
* The interactiveness in the main admin dashboard is stored in ```static/script.js```
* The script activating the quill rich text editor is stored in ```static/quillscript.js```

## Stuff Used

* Flask
* Sqlite
* [Quill](https://quilljs.com)
* Jquery
