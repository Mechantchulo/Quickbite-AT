# QuickBite USSD API

FastAPI backend for:
- Africa's Talking USSD menu flow
- PayHero STK push initiation
- PayHero payment callback handling
- USSD end-session event capture

## Features

- USSD menu:
  - Choose item
  - Enter quantity
  - Confirm/cancel
- Order persistence (`orders`)
- STK push request on confirm
- Payment status updates via callback (`PAID` / `FAILED`)
- End-of-session analytics (`ussd_session_events`)

## Project Structure

```text
Quickbite/
  app/
    api/v1/endpoints/
      ussd.py
      payments.py
    core/
      config.py
    db/
      base.py
      session.py
    models/
      order.py
      ussd_session_event.py
    services/
      ussd_service.py
      payment_service.py
  alembic/
  alembic.ini
  requirements.txt
  README.md
```

## Requirements

- Python 3.11+
- PostgreSQL
- ngrok (or any public tunnel) for callbacks

Install dependencies:

```bash
cd Quickbite
pip install -r requirements.txt
```

## Environment Variables

Create `/home/erick/Desktop/projects/AT-API/.env` (or use `.env.example`) with:

```env
APP_NAME=QuickBite USSD
APP_ENV=development
APP_DEBUG=false

DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/quickbite

AT_USERNAME=sandbox
AT_API_KEY=your_at_api_key
AT_AUTH_TOKEN=
AT_SERVICE_CODE=servicecode
AT_USSD_CALLBACK_URL=https://<public-domain>/api/v1/ussd
AT_USSD_EVENT_CALLBACK_URL=https://<public-domain>/api/v1/ussd/events

PAYHERO_BASIC_AUTH=Basic <base64_credentials>
API_USERNAME=optional
API_PASSWORD=optional
CHANNEL_ID=
URL=https://backend.payhero.co.ke/api/v2/payments
PROVIDER=m-pesa
CALLBACK_URL=https://<public-domain>/api/v1/payments/callback

# Optional endpoint protection
INTERNAL_API_KEY=
PAYHERO_CALLBACK_TOKEN=
```

## Database Setup

Create DB and run migrations:

```bash
alembic -c alembic.ini upgrade head
```

Generate a new migration after model changes:

```bash
alembic -c alembic.ini revision --autogenerate -m "describe change"
alembic -c alembic.ini upgrade head
```

## Run the API

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

- `POST /api/v1/ussd`
  - Africa's Talking interactive callback
  - Expects `application/x-www-form-urlencoded`
  - Returns `CON ...` or `END ...` text

- `POST /api/v1/ussd/events`
  - Africa's Talking end-session callback
  - Persists event into `ussd_session_events`

- `POST /api/v1/payments/stk-push`
  - Manual STK trigger endpoint
  - If `INTERNAL_API_KEY` is set, send header:
    - `x-api-key: <INTERNAL_API_KEY>`

- `POST /api/v1/payments/callback`
  - PayHero callback endpoint
  - Updates order status
  - If `PAYHERO_CALLBACK_TOKEN` is set, send header:
    - `x-callback-token: <PAYHERO_CALLBACK_TOKEN>`

## Africa's Talking Sandbox Setup

1. Start API and ngrok:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
ngrok http 8001
```

2. In AT dashboard (`USSD -> Service Codes`) set:
- Callback URL: `https://<ngrok-domain>/api/v1/ussd`
- Events URL: `https://<ngrok-domain>/api/v1/ussd/events`

3. In AT Simulator dial your mapped shared code:
- Example: `*384*6235#`

## Quick Manual Tests

Initial menu:

```bash
curl -X POST https://<ngrok-domain>/api/v1/ussd \
  -d "sessionId=1&serviceCode=*384*6235#&phoneNumber=254700000000&networkCode=63902&text="
```

Expected response starts with `CON QuickBite`.

Manual STK test:

```bash
curl -X POST http://127.0.0.1:8001/api/v1/payments/stk-push \
  -H "Content-Type: application/json" \
  -d '{"amount":20,"phone_number":"+2547XXXXXXXX","external_reference":"test-1","customer_name":"Erick"}'
```

## Known Operational Notes

- USSD sessions must respond within ~10 seconds.
- If ngrok restarts, callback URLs change and must be updated in AT/PayHero.
- Physical phone USSD testing needs live production service code; sandbox is simulator-based.
- PayHero may reject STK with account/channel errors (for example insufficient merchant/channel balance).
