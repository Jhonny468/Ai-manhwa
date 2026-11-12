# Architecture and database plan

## Production services
- Web: Next.js App Router + TypeScript.
- Android: Expo / React Native; same authenticated FastAPI API.
- API: FastAPI, Pydantic validation, SQLAlchemy 2, Alembic.
- Story orchestration: queued jobs (Celery + Redis); idempotent tasks and retry policies.
- AI gateway: provider adapters for text, image generation, image editing, embeddings and OCR. Store provider/model/version with every generation.
- Data: PostgreSQL for relational state; S3-compatible private object storage for source files, reference images, panels and exports.
- Realtime: WebSocket or SSE job progress.

## Core pipeline
Novel import -> text extraction/OCR -> chapter segmentation -> chapter summaries -> story bible -> character/location/object extraction -> scene breakdown -> shot list -> image generation -> lettering/layout -> quality checks -> chapter export.

Every stage writes versioned records. A user edit creates a new version rather than destroying the previous approved output. Downstream jobs record the versions they consumed, enabling selective regeneration.

## Database entities
- users: id, email, password_hash/auth_provider, created_at
- projects: id, owner_id, title, language, art_style_id, status, created_at
- novel_documents: id, project_id, filename, object_key, mime_type, checksum, word_count, status
- chapters: id, project_id, source_document_id, chapter_number, title, source_text, summary, status
- characters: id, project_id, canonical_name, description, visual_bible_json, reference_asset_id
- character_aliases: id, character_id, alias
- locations: id, project_id, name, description, visual_bible_json, reference_asset_id
- story_objects: id, project_id, name, description, visual_bible_json, reference_asset_id
- scenes: id, chapter_id, sequence_no, source_excerpt, summary, location_id, continuity_notes
- scene_characters: scene_id, character_id, role, emotion, action, costume_state
- panels: id, scene_id, sequence_no, shot_type, prompt, dialogue_json, status, approved_asset_id
- assets: id, project_id, asset_type, object_key, mime_type, width, height, checksum, created_at
- generations: id, project_id, panel_id, provider, model, prompt, parameters_json, status, cost_estimate, error, created_at
- style_presets: id, owner_id nullable, name, style_prompt, palette_json, linework_settings_json
- jobs: id, project_id, job_type, status, progress, attempts, error, created_at, updated_at
- exports: id, project_id, chapter_id, format, object_key, status, created_at
- audit_events: id, user_id, project_id, action, entity_type, entity_id, created_at

Use UUID primary keys, foreign keys with deliberate delete rules, indexes on owner/project/status and unique constraints for chapter_number per project and sequence_no per scene/chapter.

## Phase 1 schema implemented
`projects`, `novel_documents`, and `story_analyses` are implemented in `backend/app/models/entities.py`. Later tables should be introduced with Alembic migrations as features are added.

## Suggested repository layout

```text
manhwaforge/
  apps/
    web/                 # Next.js studio
    android/             # Expo app
  backend/
    app/
      api/               # REST routes
      core/              # settings, security
      db/                # session, base
      models/            # SQLAlchemy models
      schemas/            # Pydantic contracts
      services/           # parser, AI adapters, pipeline stages
      workers/            # Celery tasks
    migrations/           # Alembic
    tests/
  packages/
    contracts/            # shared API schemas/types
    ui/                   # shared design tokens/components
  infra/                  # Docker, deployment, monitoring
  docs/
```
