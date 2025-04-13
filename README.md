# Reprise
Enhance learning retention with spaced repetition. This project contains a React app served by a Flask API.

## Setup
Install python dependencies with [pipenv](https://pipenv.pypa.io/en/latest/) and start the web server:
```
flask --app reprise.api run
```

From the `/ui` directory, install node dependencies with `npm install` and start the React app:
```
npm start
```

### OpenAI Integration
This project uses OpenAI  models to to generate content. To enable this feature:

1. Copy the `.env.example` file to `.env`
2. Add your OpenAI API key to the `.env` file

### Database migrations
This project uses alembic for migrations. Run them from the console like so:
```
PYTHONPATH=. alembic <...>
```

### Logfire Integration
Optionally create a [logfire project](https://logfire.pydantic.dev/docs/#logfire) for model tracing. Add `LOGFIRE_TOKEN` to `.env`.
Additionally copy `/ui/.env.example` to `/ui/.env` and set the project URL.

## Email scheduling (for Mac)
Leverage [Mailgun](https://www.mailgun.com/) and Mac `launchctl` to schedule reprisal emails in lieu of a deployed backend or task executor.

1. Copy `dispatch_example.plist` to `reprise.plist`, edit labeled parameters
2. `launchctl load reprise.plist`

Unload with `launchctl unload reprise.plist` as necessary
