# Application endpoints
Server-rendered form endpoints include `POST /auth/register`, `POST /auth/login`, `POST /learn/lessons/<id>/complete`, `POST /learn/modules/<slug>/quiz`, and administrator CRUD endpoints under `/admin`. All state-changing endpoints require CSRF tokens and session authentication where applicable.
