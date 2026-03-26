# Backend Module

Backend is the system control layer of this project.

It handles authentication, CRUD APIs, resume upload orchestration, async processing, scoring integration, feedback capture, retraining triggers, and notification delivery.

## 1. Backend responsibilities

1. Expose REST APIs used by frontend.
2. Validate incoming data.
3. Enforce authentication/authorization.
4. Store and query MongoDB documents.
5. Start async AI pipeline for heavy processing.
6. Save scoring results and statuses.
7. Send candidate emails.
8. Persist recruiter feedback and trigger model retraining checks.

## 2. Folder structure and deep file guide

Top-level files:
1. `run.py`
Purpose: Flask startup entrypoint.
2. `start_backend.ps1`
Purpose: convenience script for local backend boot.
3. `.env` and `.env.example`
Purpose: runtime configuration and portable template.
4. `requirements.txt`
Purpose: module-level dependency reference.

Core app package:
1. `app/__init__.py`
Purpose: app factory, blueprint registration, app bootstrapping.
2. `app/config.py`
Purpose: env mapping to typed config values.
3. `app/extensions.py`
Purpose: shared extension objects and initialization helpers.

Routes:
1. `app/routes/company_routes.py`
Purpose: register/login/profile/settings/password flows.
2. `app/routes/job_routes.py`
Purpose: create/list/update/delete jobs.
3. `app/routes/application_routes.py`
Purpose: apply endpoint, async status polling, resume download, feedback intake.
4. `app/routes/feedback_routes.py`
Purpose: feedback management and stats endpoints.
5. `app/routes/admin_routes.py`
Purpose: admin/ops utilities.
6. `app/routes/health_routes.py`
Purpose: health checks and uptime checks.

Services:
1. `app/services/application_service.py`
Purpose: application-related business operations.
2. `app/services/company_service.py`
Purpose: company entity operations.
3. `app/services/job_service.py`
Purpose: job lifecycle operations.
4. `app/services/auth_service.py`
Purpose: auth logic and credential handling.
5. `app/services/storage_service.py`
Purpose: upload storage, temporary text output, file management.
6. `app/services/pipeline_service.py`
Purpose: bridge Backend with Resume Parser, NLP, and AI Scoring.
7. `app/services/email_service.py`
Purpose: SMTP mail sending with retries.
8. `app/services/feedback_service.py`
Purpose: feedback validation/persistence/analytics.
9. `app/services/admin_service.py`
Purpose: admin-level cleanup/report style helpers.

Utilities:
1. `app/utils/auth_middleware.py`
Purpose: token validation and protected-route checks.
2. `app/utils/validators.py`
Purpose: reusable payload validation helpers.
3. `app/utils/resume_validator.py`
Purpose: resume content sanity validation.
4. `app/utils/email_queue.py`
Purpose: optional background email queue worker.
5. `app/utils/logging.py`
Purpose: logging setup conventions.
6. `app/utils/redis_limiter.py`
Purpose: optional Redis-backed rate limit utility.
7. `app/utils/ttl_indexes.py`
Purpose: Mongo TTL index helpers.
8. `app/utils/secrets.py`
Purpose: secret-loading helper logic.

## 3. End-to-end request path inside backend

Generic request path:
1. HTTP request enters route.
2. Route validates auth and payload.
3. Route calls service layer.
4. Service reads/writes MongoDB and filesystem.
5. Service returns domain result.
6. Route builds API response JSON.

Apply flow (critical path):
1. Candidate submits job application with resume.
2. Backend saves PDF in storage.
3. Backend inserts initial application with `processing` status.
4. Backend starts background thread.
5. Thread executes PipelineService.
6. Pipeline runs parser -> NLP -> scoring.
7. Backend updates final status and score fields.
8. If selected, backend attempts email delivery.

## 4. Async pipeline and why it matters

Without async processing, request timeout risk increases because parsing and NLP can take noticeable time.

Current behavior:
1. Apply API returns immediately with `processing` status.
2. Frontend polls status endpoint.
3. Backend updates record after pipeline completion.

This gives stable UX and protects API responsiveness.

## 5. Data model overview (MongoDB)

Main collections:
1. `companies`
Contains company identity, config, and optional email templates.
2. `jobs`
Contains title, description, requirements, and owning company.
3. `applications`
Contains candidate details, score breakdown, status, rank metadata.
4. `feedback`
Contains labeled recruiter decision records used for retraining.

## 6. Configuration guide

Key env variables:
1. `SECRET_KEY`
Used for token/signing security.
2. `MONGO_URI`, `MONGO_DB`
Database connectivity.
3. `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TLS`
Email transport configuration.
4. `SCORE_THRESHOLD`
Global selection threshold.
5. `FEEDBACK_RETRAIN_THRESHOLD`
How frequently retrain check is triggered.
6. `FEEDBACK_MIN_TRAIN_SAMPLES`
Minimum feedback count before training.

Important SMTP note:
For Gmail, set `SMTP_HOST=smtp.gmail.com` and use app password in `SMTP_PASSWORD`.

## 7. Error handling and resilience

1. Input validation errors return clear 4xx responses.
2. Pipeline failures are isolated to application status updates.
3. Email send failures do not crash full request flow.
4. Defensive logging helps trace route/service failures.

## 8. Security model summary

1. Token-auth middleware for protected APIs.
2. Env-based secret loading.
3. Validation on user-controlled fields.
4. Optional rate-limit and TTL controls.

## 9. Troubleshooting checklist

If apply is stuck in `processing`:
1. Check backend logs for parser/NLP/scoring exception.
2. Verify storage path write permissions.
3. Verify module import paths for parser/NLP/scoring.

If selected emails are not sent:
1. Verify SMTP env values.
2. Ensure selected status is actually reached by threshold.
3. Check email service logs for login/connect errors.

If feedback retraining never starts:
1. Check `FEEDBACK_RETRAIN_THRESHOLD` value.
2. Check `FEEDBACK_MIN_TRAIN_SAMPLES` and class balance.
3. Verify feedback documents are being inserted.

## 10. Extension points

1. Replace thread-based async with Celery/RQ workers.
2. Add robust retry queue for pipeline failures.
3. Add role-based authorization layers.
4. Add OpenAPI spec generation for route contracts.

## 11. Interview questions and answers

1. Why route-service separation?
Answer: keeps HTTP concerns separate from business logic and improves maintainability.

2. Why asynchronous pipeline design?
Answer: heavy processing must not block API response latency.

3. Why MongoDB for this workload?
Answer: flexible schema fits evolving extraction and feedback structures.

4. How is explainability preserved?
Answer: backend stores and returns component scores, not only final decision.
