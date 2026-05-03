"""
ORQUESTADOR HIBRIDO - AI-FACTORY-v2
Pipeline flexible con:
  - Dual Generation (2 agentes compiten)
  - Judge Agent (selecciona la mejor version)
  - Human-in-the-loop (decisiones criticas)
  - Context Layer (ninguna fuente de datos expuesta directamente)
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

from context.context_layer import ContextManager, UserRole
from agents.supervisor_agent import SupervisorAgent
from agents.data_intelligence_agent import DataIntelligenceAgent
from agents.analysis_agent import AnalysisAgent
from agents.generation_agent import GenerationAgent
from agents.judge_agent import JudgeAgent
from agents.validation_agent import ValidationAgent
from agents.memory_agent import MemoryAgent
from agents.delivery_agent import DeliveryAgent


class HybridOrchestrator:
    """
    Cerebro que coordina todo el sistema multi-agente.
    Implementa el patron Context Layer como regla de oro:
    ningun agente accede directamente a datos.
    """

    def __init__(self) -> None:
        self.supervisor = SupervisorAgent()
        self.data_agent = DataIntelligenceAgent()
        self.analysis_agent = AnalysisAgent()
        self.generator1 = GenerationAgent(agent_id="generator_1", style="professional")
        self.generator2 = GenerationAgent(agent_id="generator_2", style="creative")
        self.judge = JudgeAgent()
        self.validator = ValidationAgent()
        self.memory = MemoryAgent()
        self.delivery = DeliveryAgent()
        self.context_manager = ContextManager()

    async def run(
        self,
        prompt: str,
        user_id: str,
        client: str,
        role: UserRole,
    ) -> Dict[str, Any]:
        """Punto de entrada principal del sistema agentico."""

        # 1. Crear contexto - TODO pasa por aqui
        ctx_obj = self.context_manager.create_context(
            client=client, user_id=user_id, role=role
        )
        context = ctx_obj.to_dict()

        # 2. Supervisor: detecta intencion y decide workflow
        intent = self.supervisor.detect_intent(prompt, context)
        workflow = self.supervisor.decide_workflow(intent, context)

        # 3. Data Intelligence: solo estructura datos
        data = await self.data_agent.fetch(context)

        # 4. Analysis: convierte datos en insights
        insights = await self.analysis_agent.process(data, intent.value)

        # 5. Dual Generation: 2 agentes compiten en paralelo
        draft1, draft2 = await asyncio.gather(
            self.generator1.create(insights, intent.value, context),
            self.generator2.create(insights, intent.value, context),
        )

        # 6. Judge Agent: selecciona la mejor version
        judge_result = await self.judge.evaluate([draft1, draft2], context)
        best_draft = judge_result["selected"]

        # 7. Validation Agent
        validation = await self.validator.validate(best_draft, context)

        # 8. Human-in-the-loop para decisiones criticas
        if workflow.requires_human_approval or not validation["valid"]:
            human_decision = await self._request_human_approval(
                best_draft, validation, context
            )
            if not human_decision["approved"]:
                return {
                    "status": "pending_human_review",
                    "message": "En espera de aprobacion humana.",
                    "draft": best_draft,
                    "validation": validation,
                }

        # 9. Memory Agent: guarda historico del cliente
        await self.memory.store(context, best_draft)

        # 10. Delivery Agent: publica con permisos
        delivery_result = await self.delivery.publish(best_draft, context)

        # 11. Control de calidad final por supervisor
        quality = self.supervisor.control_quality(best_draft)

        return {
            "status": "completed",
            "intent": intent.value,
            "workflow": {
                "agents_used": workflow.required_agents,
                "steps": workflow.estimated_steps,
            },
            "result": best_draft,
            "judge": {
                "scores": judge_result["all_scores"],
                "suggestions": judge_result["improvement_suggestions"],
            },
            "validation": validation,
            "delivery": delivery_result,
            "quality": quality,
            "context": context,
        }

    async def _request_human_approval(
        self,
        draft: Dict[str, Any],
        validation: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Solicita aprobacion humana para decisiones criticas.
        En produccion: envia notificacion por email/Teams y espera respuesta.
        """
        print(
            f"\n[HUMAN REVIEW REQUIRED] client={context['client']} "
            f"issues={validation.get('issues', [])}\n"
            f"  Preview: {str(draft.get('content', ''))[:120]}"
        )
        # Auto-aprobacion para entorno de desarrollo.
        # En produccion: implementar flujo async de aprobacion real.
        return {"approved": True, "reviewer": "system_auto"}
