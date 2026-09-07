import logging
import os

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    ErrorEvent,
    JobContext,
    UserInputTranscribedEvent,
    UserStateChangedEvent,
    inference,
)
from livekit.plugins import deepgram, elevenlabs, openai

load_dotenv()

logger = logging.getLogger("phone-agent")

# Keep only one warm process. The production default prewarms one per CPU,
# which exceeds small hosting memory limits.
server = AgentServer(num_idle_processes=1)

@server.rtc_session(agent_name="phone-agent")
async def entrypoint(ctx: JobContext):
    agent = Agent(
        instructions=(
            "You are a friendly voice assistant. Keep every reply to one or "
            "two short sentences, since your words are spoken out loud."
        )
    )

    session = AgentSession(
        stt=deepgram.STTv2(
            model="flux-general-en",
            eager_eot_threshold=0.4,
        ),

        llm=openai.responses.LLM(model="gpt-4.1-mini"),

        # llm=inference.LLM(model="google/gemma-4-31b-it"),
        tts=elevenlabs.TTS(
            voice_id="ODq5zmih8GrVes37Dizd",
            model="eleven_turbo_v2_5",
            api_key=os.environ["ELEVENLABS_API_KEY"],
        ),
    )

    @session.on("user_input_transcribed")
    def _on_transcript(ev: UserInputTranscribedEvent) -> None:
        logger.info("heard caller: final=%s len=%d", ev.is_final, len(ev.transcript))

    @session.on("user_state_changed")
    def _on_user_state(ev: UserStateChangedEvent) -> None:
        logger.info("caller state: %s -> %s", ev.old_state, ev.new_state)

    @session.on("error")
    def _on_error(ev: ErrorEvent) -> None:
        logger.error(
            "session error from %s (recoverable=%s): %s",
            type(ev.source).__name__,
            ev.error.recoverable,
            ev.error,
        )

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="Greet the user and ask how you can help."
    )

if __name__ == "__main__":
    agents.cli.run_app(server)
