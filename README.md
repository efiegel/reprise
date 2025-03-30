# Reprise
Enhance learning retention with spaced repetition. This project contains a React app served by a Flask API.

## Setup
Install python dependencies with [pipenv](https://pipenv.pypa.io/en/latest/) and start the web server:
```
flask --app reprise.api run
```

From the `/frontend` directory, install node dependencies with `npm install` and start the React app:
```
npm start
```

### OpenAI Integration
This project uses OpenAI's GPT-4o-mini model to automatically generate cloze deletions for your motifs. To enable this feature:

1. Copy the `.env.example` file to `.env`
2. Add your OpenAI API key to the `.env` file
3. Optionally change the model by setting `OPENAI_MODEL`

If no API key is provided, the application will fall back to a simple default cloze deletion.

### Database migrations
This project uses alembic for migrations. Run them from the console like so:
```
PYTHONPATH=. alembic <...>
```
