# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import logging
from typing import Optional, Union, Any, List

from a2a.server.apps.kafka import KafkaServerApp
from a2a.server.request_handlers.kafka_handler import KafkaHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from google.adk.agents.base_agent import BaseAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder

logger = logging.getLogger(__name__)

def _load_agent_card(
    agent_card: Optional[Union[AgentCard, str]],
) -> Optional[AgentCard]:
  """Load agent card from various sources.

  Args:
      agent_card: AgentCard object, path to JSON file, or None

  Returns:
      AgentCard object or None if no agent card provided

  Raises:
      ValueError: If loading agent card from file fails
  """
  if agent_card is None:
    return None

  if isinstance(agent_card, str):
    # Load agent card from file path
    import json
    from pathlib import Path

    try:
      path = Path(agent_card)
      with path.open("r", encoding="utf-8") as f:
        agent_card_data = json.load(f)
        return AgentCard(**agent_card_data)
    except Exception as e:
      raise ValueError(
          f"Failed to load agent card from {agent_card}: {e}"
      ) from e
  else:
    return agent_card


async def create_kafka_server(
    agent: BaseAgent,
    *,
    bootstrap_servers: str | List[str] = "bootstrap.mission-charlie-kafka.us-central1.managedkafka.pokedemo-test.cloud.goog:9092",
    request_topic: str = "a2a-requests",
    consumer_group_id: str = "a2a-agent-group",
    agent_card: Optional[Union[AgentCard, str]] = None,
    runner: Optional[Runner] = None,
    **kafka_config: Any,
) -> KafkaServerApp:
  """Convert an ADK agent to a A2A Kafka Server application.

  Args:
      agent: The ADK agent to convert
      bootstrap_servers: Kafka bootstrap servers.
      request_topic: Topic to consume requests from.
      consumer_group_id: Consumer group ID for the server.
      agent_card: Optional pre-built AgentCard object or path to agent card
                  JSON. If not provided, will be built automatically from the
                  agent.
      runner: Optional pre-built Runner object. If not provided, a default
              runner will be created using in-memory services.
      **kafka_config: Additional Kafka configuration.

  Returns:
      A KafkaServerApp that can be run with .run() or .start()
  """
  # Set up ADK logging
  adk_logger = logging.getLogger("google_adk")
  adk_logger.setLevel(logging.INFO)

  async def create_runner() -> Runner:
    """Create a runner for the agent."""
    return Runner(
        app_name=agent.name or "adk_agent",
        agent=agent,
        # Use minimal services - in a real implementation these could be configured
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
    )

  # Create A2A components
  task_store = InMemoryTaskStore()

  agent_executor = A2aAgentExecutor(
      runner=runner or create_runner,
  )
  
  # Initialize logic handler
  from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
  
  logic_handler = DefaultRequestHandler(
      agent_executor=agent_executor, task_store=task_store
  )

  # Prepare Agent Card
  rpc_url = f"kafka://{bootstrap_servers}/{request_topic}"
  provided_agent_card = _load_agent_card(agent_card)

  card_builder = AgentCardBuilder(
      agent=agent,
      rpc_url=rpc_url,
  )
  
  if provided_agent_card is None:
      # Build the card to ensure it's valid, though we don't strictly pass it to KafkaServerApp currently
      # (KafkaServerApp might rely on the handler having context, but DefaultRequestHandler is generic)
      await card_builder.build()
      
  # Create Kafka Server App
  server_app = KafkaServerApp(
      request_handler=logic_handler,
      bootstrap_servers=bootstrap_servers,
      request_topic=request_topic,
      consumer_group_id=consumer_group_id,
      **kafka_config
  )
  
  return server_app
