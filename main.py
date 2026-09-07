import os

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, JobContext, inference
from livekit.plugins import deepgram, elevenlabs, openai

load_dotenv()

server = AgentServer()

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

    await session.start(agent=agent, room=ctx.room)
    await session.generate_reply(
        instructions="Greet the user and ask how you can help."
    )

if __name__ == "__main__":
    agents.cli.run_app(server)
