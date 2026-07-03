import json
import re

class JSONLogHealer:
    def try_heal(self, raw_data: str) -> tuple[dict | None, list[str]]:
        """
        Intenta reparar problemas comunes de JSONs generados por LLMs.
        Retorna (dict_reparado, lista_de_estrategias_aplicadas)
        """
        strategies = []
        cleaned = raw_data.strip()

        # Estrategia 1: Extraer JSON si el LLM incluyó texto explicativo o Markdown bloques
        if not cleaned.startswith("{"):
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                cleaned = match.group(0)
                strategies.append("Extracción de bloque interno (Regex)")

        # Estrategia 2: Intentar parseo directo
        try:
            return json.loads(cleaned), strategies
        except json.JSONDecodeError:
            pass

        # Estrategia 3: El LLM se cortó a la mitad y falta cerrar la llave principal
        if cleaned.startswith("{") and not cleaned.endswith("}"):
            # Caso común de falta de tokens de salida
            try:
                test_heal = cleaned + "}"
                parsed = json.loads(test_heal)
                strategies.append("Cierre forzado de llave truncada ('}')")
                return parsed, strategies
            except json.JSONDecodeError:
                pass

        # Si ninguna heurística funciona, el log es insalvable
        return None, strategies