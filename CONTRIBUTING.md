# Contributing

Follow the README's locked setup. Describe the problem, user-visible result, and verification in a pull request. Keep source documents and credentials out of fixtures and logs.

Run backend tests, Ruff, and pip-audit; run frontend typechecking, production build, and npm audit. For migrations or deployment changes, also build Compose and run the smoke check on a disposable workspace. Tests use an independent in-memory database.

For schema changes, add an Alembic revision and explain backup/reindex needs. Do not change embedding models or dimensions without a compatibility plan. New features should state whether they require third-party services or send documents outside the host.

The project has no selected license. Discuss redistribution/licensing with the owner before treating it as a licensed open-source dependency.
