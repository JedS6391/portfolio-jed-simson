# Portfolio

## About

A Python 3 web application, built using Flask to serve my portfolio.

The deployed application can be viewed [here](https://www.jedsimson.co.nz/).

### Features

- Landing page
- About section
- Project feed
- Blog
- Contact form

### Stack

#### App

- [Python 3](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [Halfmoon UI](https://www.gethalfmoon.com/)
- [Feather Icons](https://feathericons.com/)
- [SendGrid](https://sendgrid.com/)

#### Deployment

- [gunicorn](https://gunicorn.org/)
- [Docker](https://www.docker.com/)
- [Render](https://www.render.com/)

## Development

Follow the instructions below to get started with the app in a local development environment.

### Prerequisites

- [Docker](https://www.docker.com/get-started)

### Running

The app can be run via `docker` with the following commands:

```console
# Build image
docker build -t portfolio-jed-simson .
 
# Run in container
docker run --env-file=.env -p=8000:5000 portfolio-jed-simson
```

*Note that an environment file will need to be provided to define the environment variables required by the app. The full list of variables is listed below.*

| Name                      | Description                                                                                                                      | Required           |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `APP_SETTINGS`            | Defines the configuration the app should run with. Supported values are `config.DevelopmentConfig` or `config.ProductionConfig`. | :x:                |
| `SECRET_KEY`              | Secret key used by some of the app libraries.                                                                                    | :white_check_mark: |
| `POSTS_PATH`              | Path used to load blog posts from. Default value is `static/assets/posts/`.                                                      | :x:                |
| `POSTS_PER_PAGE`          | Max number of posts to show on a blog page. Default value is `10`.                                                               | :x:                |
| `PROJECT_FEED_PATH`       | Path used to load projects in the project feed from. Default value is `static/assets/projects/project_feed.json`.                | :x:                |
| `SENDGRID_API_KEY`        | API key for SendGrid email integration.                                                                                          | :white_check_mark: |
| `SENDGRID_DEFAULT_FROM`   | Email address used in the 'From' email field when sending messages from the contact form.                                        | :white_check_mark: |
| `CONTACT_EMAIL`           | Email address that messages in the contact form will be sent to.                                                                 | :white_check_mark: |
| `RECAPTCHA_PUBLIC_KEY`    | Public key used by ReCAPTCHA in the contact form.                                                                                | :white_check_mark: |
| `RECAPTCHA_PRIVATE_KEY`   | Private key used by ReCAPTCHA in the contact form.                                                                               | :white_check_mark: |
| `RECAPTCHA_DATA_ATTRS`    | Optional attributes that will be passed to the ReCAPTCHA component.                                                              | :x:                |
| `LOG_LEVEL`               | Log level used by the app. See [logging levels](https://docs.python.org/3/library/logging.html#logging-levels)                   | :white_check_mark: |
| `SENTRY_DSN`              | DSN for Sentry integration.                                                                                                      | :white_check_mark: |
| `CONTENT_SECURITY_POLICY` | Content security policy used by the app.                                                                                         | :x:                |