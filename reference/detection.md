# Detection rules

Each condition key used in `reference/asvs-checks.md` and `reference/additional-practices.md` has a predicate below. Every predicate can be checked with file search and `grep` only: manifest dependencies, file globs, config keys, route and middleware names. Do not run the application and do not install anything.

Read manifests and lock files before grepping source. A match in a dependency manifest is a strong signal; a match only in source code (an import, a function call) is also enough. A match only in `tests/`, `docs/`, `examples/` or vendored folders (`vendor/`, `node_modules/`) is not.

For each key, record `detected` or `not detected` with the evidence (path:line or the search with hit count). **Detected** means the predicate holds: the group of checks tied to the key applies. **Not detected** means the search was run and found nothing: every check tied to the key is `n/a`, with the reason "condition `<key>` not detected" and the search cited. When a search is inconclusive (for example a dynamic include you could not resolve), say so and ask the user in the scope confirmation instead of guessing.

## Nested layouts

The application may live in a subfolder (for example `src/`, `app/`, `backend/`, `services/api/`) with manifests, config and Dockerfiles below the repository root. Start every search from the repository root. Find manifests first (`composer.json`, `package.json`, `pyproject.toml`, `requirements*.txt`, `manage.py`, `artisan`), record the application root(s) where they live, and run the predicates against the whole tree, excluding `vendor/`, `node_modules/`, `.venv/` and build output. A monorepo has several application roots; apply each predicate per root and say which root a finding belongs to. Cite paths from the repository root.

## Project picture

Write one paragraph that describes the project before judging any check. Read, in this order:

- Manifests and lock files: `composer.json` and `composer.lock`, `package.json` and its lock file, `pyproject.toml`, `Pipfile.lock`, `requirements*.txt`, `poetry.lock`, `Cargo.lock`, `go.mod`.
- Framework config: `config/` (Laravel), `settings.py` (Django), `app.py` or `config.py` (Flask), `nest-cli.json`, `next.config.*`, `symfony` `config/packages/`.
- Routes and entry points: `routes/`, `urls.py`, `app.use(` and `router.` in the Node entry file, controller folders.
- Migrations and models: `database/migrations/`, `*/migrations/`, `prisma/schema.prisma`, `models/`.
- Deployment: `Dockerfile*`, Compose files, `.env.example`, web server config, `Procfile`, Kubernetes manifests, deploy scripts.
- CI: `.github/workflows/`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`, `.circleci/`, `Jenkinsfile`.
- `README.md` and `docs/` for what the product does and who uses it.

The paragraph must name: language and framework with versions taken from the lock files (cite the lock file line, not the version range in the manifest); the database; the authentication mechanism (own login, external provider, token); the deployment shape (container, plain server, serverless, static hosting); and the CI system. If a fact cannot be found, write "not found" rather than guessing.

## Conditions

### own-auth
The application implements its own login and credential handling.
Detected when any of these holds. PHP/Laravel: `composer.json` requires `laravel/breeze`, `laravel/fortify`, `laravel/jetstream`, `laravel/ui` or `laravel/sanctum` with a login route, or `routes/` contains `Auth::routes(` or a login controller that calls `Auth::attempt(` or `Hash::check(`; Symfony `security.yaml` with a `form_login` or `json_login` firewall. Node: `passport-local`, `bcrypt`, `bcryptjs` or `argon2` in `package.json`, or a route handler comparing a submitted password to a stored hash. Python: Django `django.contrib.auth` with `authenticate(` or `LoginView`, `django-allauth`, Flask-Login with a password check, `fastapi-users`. A `password` column in a users migration is not enough on its own; the confirming signal is a login route or handler (Fortify, Breeze or Jetstream login routes, `Auth::routes`, Django `LoginView` or `django.contrib.auth.urls`, a Passport local strategy, a POST login route that checks a password).
Not detected when login is only through an external provider (`idp`, `oauth-client` hits) or the application has no accounts.

### rich-text
Users submit HTML, for example from a WYSIWYG editor.
Detected when `package.json` depends on an editor (`tinymce`, `ckeditor`, `quill`, `@tiptap/*`, `trix`, `summernote`, `draft-js`, `slate`, `lexical`) or templates load one; PHP `composer.json` requires `mews/purifier`, `ezyang/htmlpurifier` or `stevebauman/purify`; Python uses `bleach`, `nh3` or `django-ckeditor`; or code stores and later outputs unescaped HTML fields (Blade `{!! $post->body !!}`, Twig `|raw`, Jinja `|safe` on stored content, `dangerouslySetInnerHTML`, `v-html` fed from an API).
Not detected when no editor and no raw output of user-supplied HTML exists. Markdown rendering that sanitizes output counts only if it is itself the input path; note it.

### outbound-urls
Server code requests URLs that users can influence.
Detected when server code makes HTTP requests whose URL, host or path comes (even partly) from request data, a stored URL field, a webhook configuration or an uploaded file. Search PHP `Http::get(`, `file_get_contents('http`, `curl_init(`, Guzzle `->request(`; Node `fetch(`, `axios`, `got(`, `http.get(`, `request(`, `node-fetch`; Python `requests.get(`, `httpx`, `urllib.request`, `aiohttp`. Features: webhooks, link previews, URL import, avatar-by-URL, image proxy, PDF generation from a URL (`wkhtmltopdf`, `puppeteer` `page.goto(`), RSS fetch, OAuth discovery from a user-supplied issuer.
Not detected when all outbound request URLs are constants or come from deployment config only. Cite the search and hit count.

### mail
The application sends or reads mail using user-supplied values.
Detected when the code sends mail with a recipient, subject, header or body taken from user input. Search PHP `Mail::to(`, `mail(`, `Mailable`, Symfony Mailer, PHPMailer `addAddress(`; Node `nodemailer`, `sendmail`, `@sendgrid/mail`, `mailgun`; Python `send_mail(`, `EmailMessage`, `smtplib`, `flask-mail`; and IMAP or POP reading (`imap_open(`, `imaplib`, `imapflow`). A contact form, invite, share-by-email or reply-to feature qualifies.
Not detected when mail is only sent to fixed internal addresses with fixed content, or no mail code exists.

### xml
The application parses XML.
Detected when code or dependencies parse XML. PHP: `simplexml_load_string(`, `DOMDocument`, `XMLReader`, `xml_parse(`, `libxml_`; Node: `xml2js`, `fast-xml-parser`, `libxmljs`, `xmldom`, `sax`; Python: `xml.etree`, `lxml`, `xml.dom.minidom`, `defusedxml`, `xmltodict`; also SAML libraries, SOAP clients and servers, SVG or Office document handling, and RSS parsing. Check config and uploads that accept `.xml`, `.svg`, `.docx`, `.xlsx`.
Not detected when no XML parsing call, XML-based library or XML upload exists. JSON-only APIs are not detected.

### graphql
The application exposes a GraphQL API.
Detected when the repository defines a GraphQL endpoint. PHP: `nuwave/lighthouse`, `rebing/graphql-laravel`, `webonyx/graphql-php`, `api-platform` with GraphQL; Node: `graphql`, `apollo-server`, `@apollo/server`, `graphql-yoga`, `mercurius`, `type-graphql`, `@nestjs/graphql`; Python: `graphene`, `strawberry-graphql`, `ariadne`; files `*.graphql`, `schema.graphql`, a `/graphql` route.
Not detected when none of these exist. A GraphQL client only (calling a third-party API) is not detected.

### uploads
The application accepts file uploads.
Detected when the code receives files. PHP: `$_FILES`, `$request->file(`, `UploadedFile`, `->store(`, `move_uploaded_file(`; Node: `multer`, `busboy`, `formidable`, `express-fileupload`, `@nestjs/platform-express` `FileInterceptor`; Python: Django `FileField`, `ImageField`, `request.FILES`, Flask `request.files`, `FastAPI` `UploadFile`; HTML `<input type="file"`; pre-signed upload URLs to object storage also count.
Not detected when none of these exist.

### mfa
The application offers or requires multi-factor authentication.
Detected when the code implements or integrates a second factor. PHP: `pragmarx/google2fa`, `spomky-labs/otphp`, Fortify two-factor features (`two_factor_secret` column), `web-auth/webauthn-lib`; Node: `speakeasy`, `otplib`, `@simplewebauthn/server`, `passport-totp`; Python: `pyotp`, `django-otp`, `django-two-factor-auth`, `webauthn`, `fido2`. Also columns or fields named `totp_secret`, `two_factor_*`, `recovery_codes`. A package or column alone is not enough: the feature must be enabled in config or routes (for example Fortify `Features::twoFactorAuthentication()`, an enrollment or verification route, `django-otp` in `INSTALLED_APPS` and middleware).
Not detected when none of these exist. MFA performed only by an external identity provider is covered by `idp`, not by this key.

### idp
The application delegates login to an external identity provider.
Detected when login is done through SAML, OIDC or social sign-in. PHP: `laravel/socialite`, `socialiteproviders/*`, `onelogin/php-saml`, `simplesamlphp`; Node: `passport-saml`, `passport-google-oauth20`, `passport-azure-ad`, `openid-client`, `next-auth`, `@auth0/*`, `keycloak-connect`; Python: `python3-saml`, `django-allauth` socialaccount providers, `social-auth-app-django`, `authlib`, `mozilla-django-oidc`. Config keys naming an issuer, tenant or client id for sign-in.
Not detected when there is no external sign-in. Calls to third-party APIs that are not about login are not detected.

### multi-tenant
One deployment serves several tenants or organisations.
Detected when data is partitioned by tenant. Search `tenant_id`, `organization_id`, `org_id`, `team_id`, `account_id` columns in migrations and models; packages `stancl/tenancy`, `spatie/laravel-multitenancy`, `django-tenants`, `django-tenant-schemas`; global scopes or middleware that set a tenant (`TenantScope`, `setTenant`, `current_tenant`); subdomain-per-customer routing; a `tenants` or `organizations` table with membership.
Not detected when the application has a single owner, or users only own personal data with no shared organisational scope.

### jwt
The application issues or verifies JSON Web Tokens or other self-contained tokens.
Detected when `composer.json` requires `laravel/passport`, `firebase/php-jwt`, `lcobucci/jwt`, `tymon/jwt-auth` or `web-token/*`; `package.json` depends on `jsonwebtoken`, `jose`, `passport-jwt`, `@nestjs/jwt`, `jwt-decode` used server side; Python depends on `PyJWT`, `python-jose`, `djangorestframework-simplejwt`, `authlib` with JOSE, `fastapi` JWT helpers; or code builds or reads a three-part token (`eyJ` literals, `Bearer` parsing followed by decode). Laravel Sanctum alone issues opaque tokens and is not detected.
Not detected when none of these exist.

### oauth-client
The application acts as an OAuth or OIDC client.
Detected when the application redirects users to a provider or calls a provider with a code or token. PHP: `laravel/socialite`, `league/oauth2-client`; Node: `passport-oauth2`, `openid-client`, `simple-oauth2`, `next-auth`, `oauth` packages, `client_id` and `redirect_uri` in code; Python: `authlib`, `requests-oauthlib`, `social-auth-app-django`, `django-allauth`. An authorization-code callback route (`/callback`, `/oauth/callback`, `/auth/*/callback`) also counts. Acting as the OAuth server only (Passport issuing tokens to others) is not detected here.
Not detected when none of these exist.

### webserver-config
Web server or proxy configuration is part of the repository.
Detected when the repository contains configuration for a web server or proxy that serves the application: `nginx.conf`, `nginx/*.conf`, `conf.d/*.conf`, `sites-available/*`, `default.conf`, Apache `httpd.conf`, `apache2.conf`, `*.vhost`, `.htaccess`, `Caddyfile`, `traefik.yml`, `haproxy.cfg`, Compose volumes mounting such files, Dockerfile `COPY` lines that copy them.
Not detected when none exist. A `public/.htaccess` counts (V13.4.3 reads `Options -Indexes` there). Hosting-panel settings outside the repository are not visible and are not detected.

### browser-storage
Front-end code stores data in browser storage.
Detected when front-end source (`*.js`, `*.jsx`, `*.ts`, `*.tsx`, `*.vue`, `*.svelte`, templates with inline scripts) contains `localStorage`, `sessionStorage`, `indexedDB`, `document.cookie =` writes, or persistence libraries (`redux-persist`, `localforage`, `js-cookie`, `pinia-plugin-persistedstate`, `zustand/middleware` `persist`, `ngx-webstorage`). Server-side cookies set by the back end are covered by other checks and do not count.
Not detected when the repository has no browser front end, or the search finds no storage use in code the application ships.

### node-backend
The back end runs on Node.js.
Detected when a server-side Node application exists: `package.json` with `express`, `fastify`, `koa`, `hapi`, `@nestjs/core`, `next` with API routes or server components, `sails`, `adonis`; an entry file calling `listen(`; `"main"` or a `start` script running `node`; a Dockerfile `FROM node` for the application image; serverless handlers (`exports.handler`) in Node.
Not detected when Node is used only to build the front end (webpack, Vite, Mix) and no server code runs on it, or there is no `package.json`.

### dockerfile
The repository builds container images.
Detected when files matching `**/Dockerfile*` or `**/*.dockerfile` exist (excluding `vendor/` and `node_modules/`), or a Compose `build:` key points at a context with such a file. Record the path of each.
Not detected when none exist. A Compose file that only uses prebuilt `image:` entries is not a Dockerfile match; AP-1, AP-2 and AP-5 are `n/a` (AP-2 covers `FROM` lines only), AP-3 and AP-4 still apply through `compose`.

### compose
The repository defines a Compose stack.
Detected when files matching `compose.yml`, `compose.yaml`, `compose.*.yml`, `docker-compose.yml`, `docker-compose.yaml`, `docker-compose.*.yml` or `**/docker-compose*.yml` exist (excluding `vendor/` and `node_modules/`) and contain a `services:` key. Record each file and its role (development, production, override).
Not detected when none exist. Kubernetes manifests alone are not Compose; note them in the project picture.

### ci
The repository has a CI definition.
Detected when any of these exist: `.github/workflows/*.yml` or `.yaml`, `.gitlab-ci.yml`, `bitbucket-pipelines.yml`, `.circleci/config.yml`, `Jenkinsfile`, `azure-pipelines.yml`, `.drone.yml`, `.travis.yml`, `.woodpecker.yml` or `.woodpecker/*.yml`, `buildspec.yml`. Record which system (needed for AP-11, which applies to GitHub Actions only).
Not detected when none exist; the AP-9 to AP-11 practices are then `n/a` (AP-8 is core). A CI system configured only in a hosting UI is not visible and is not detected.
