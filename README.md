# LiveKit Twilio Voice Agent

A Python LiveKit voice agent that handles incoming Twilio calls through the official LiveKit Twilio Connector.

## Runtime services

Render deploys two services from `render.yaml`:

- `livekit-twilio-webhook` is the public Twilio webhook. It creates an inbound LiveKit Connector session and returns TwiML.
- `livekit-phone-agent` is the LiveKit agent worker registered as `phone-agent`.

The webhook must be configured as the **A call comes in** URL for your Twilio number using **HTTP POST**.

## Required Render environment variables

Set these in Render. Do not commit them to Git:

- Webhook: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`
- Agent worker: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `DEEPGRAM_API_KEY`, `OPENAI_API_KEY`, `ELEVENLABS_API_KEY`

After Render creates the web service, set the Twilio inbound-call webhook URL to:

```text
https://<your-render-web-service>.onrender.com/
```

No Cloudflare Tunnel is needed in Render.

## Local commands

```powershell
python twilio_webhook.py
python main.py dev
```
