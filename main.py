from src.healer import JSONLogHealer
from src.validator import LLMLogSchema
from src.database import LogAuditDB

def run_pipeline():
    db = LogAuditDB()
    healer = JSONLogHealer()

    # Simulamos 3 respuestas distintas que llegaron del servidor del LLM en producción
    mock_llm_payloads = [
        # 1. Log Perfecto
        '{"request_id": "req_001", "prompt": "Hola", "response_text": "Mundo", "tokens_used": 15}',
        
        # 2. Log Sucio (Con texto extra de alucinación externa)
        'Claro, aquí tienes el registro: {"request_id": "req_002", "prompt": "Clima", "response_text": "Soleado", "tokens_used": 42} Espero te sirva.',
        
        # 3. Log Truncado (Cortado abruptamente al final por falta de tokens)
        '{"request_id": "req_003", "prompt": "Fintech", "response_text": "Inversión segura", "tokens_used": 105'
    ]

    print("\n[PIPELINE] Procesando transmisión de logs en tiempo real...\n")

    for idx, raw_payload in enumerate(mock_llm_payloads, 1):
        print(f"--- Evaluando Registro #{idx} ---")
        
        # 1. Intentar parsear y sanar si es necesario
        parsed_dict, applied_strategies = healer.try_heal(raw_payload)
        
        if not parsed_dict:
            print("[CRÍTICO] ❌ Formato JSON corrupto irreversible. Enviando a Dead Letter Queue.\n")
            continue

        # 2. Validar contra el contrato de datos (Pydantic)
        try:
            validated_log = LLMLogSchema(**parsed_dict)
            status = "HEALED" if applied_strategies else "PERFECT"
            strategy_str = ", ".join(applied_strategies) if applied_strategies else "None"
            
            # 3. Persistir en Base de Datos de Producción
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO clean_logs VALUES (?, ?, ?, ?, ?, ?);
                """, (validated_log.request_id, validated_log.prompt, validated_log.response_text, validated_log.tokens_used, status, strategy_str))
                conn.commit()
                
            print(f"[ESTADO] -> [{status}]")
            if applied_strategies:
                print(f"[SANACIÓN] 🩹 Estrategias: {strategy_str}")
            print(f"[ÉXITO] Relación guardada en base de datos limpia.\n")
            
        except Exception as e:
            print(f"[ERROR CONTRATO] ⚠️ Datos sanados pero no cumplen el esquema: {e}\n")

if __name__ == "__main__":
    run_pipeline()