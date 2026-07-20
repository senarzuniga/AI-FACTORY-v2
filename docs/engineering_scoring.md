# Engineering Scoring — Método inicial

Objetivo
- Evaluar hipótesis y alternativas usando una métrica compuesta y normalizada para producir un `Global Engineering Score`.

Dimensiones (ejemplo)
- Architecture (0-1)
- Maintainability (0-1)
- Scalability (0-1)
- Performance (0-1)
- Engineering Accuracy (0-1)
- Mathematical Correctness (0-1)
- Knowledge Reuse (0-1)
- Automation (0-1)
- Integration (0-1)
- Business Value (0-1)

Normalización y agregación
1. Cada dimensión se puntúa entre 0 y 1.
2. Aplicar pesos w_i definidos por prioridad del proyecto.
3. Global Engineering Score = sum(w_i * score_i) / sum(w_i)

Reglas de decisión
- Seleccionar la hipótesis con mayor `Global Engineering Score`.
- Registrar alternativas rechazadas con motivo y métricas individuales.

Próximos pasos
1. Definir pesos iniciales y umbrales de aceptación.
2. Integrar la evaluación automática en el Mission Manager (POC).
