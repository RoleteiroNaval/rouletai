import time
import sys
from datetime import datetime

from config.settings import Settings

# Sticker for terminais baguncados
TERMINAIS_BAGUNCADOS_STICKER = (
    "CAACAgEAAxkBAAEQgLNpjqgYIAkuLWqX_v-suGpSThI-SgACBQYAAmTxwEej7Igzpi1WZDoE"
)
from core.monitor import GameMonitor
from engine import (
    StrategyState,
    pre_process_strategies,
    get_optimized_strategy,
    ESTRATEGIAS,
    formatter,
)
from services.bot import TelegramBot
from services.reporting import ReportingSystem
from storage.database import Database
from analytics.metrics import Metrics, HealthMonitor
from analytics.strategy_analytics import analytics
from analytics.context_filter import ContextFilter
from analytics.strategy_performance import tracker
from storage.backup import backup_system
from utils.logger import setup_logger
from utils.history_buffer import HistoryBuffer
from utils.turbulence_monitor import TurbulenceMonitor
from analytics.transition_memory import TransitionMemory

# New agentic system
from server.agents.memory import MemoryAgent
from server.services.engine import run_engine
from server.agents.telegram import format_telegram_message

logger = setup_logger("main_visual")


def run_bot():
    """Execução principal do bot com lógica de sessão"""
    logger.info("=" * 60)
    logger.info("BOT INICIADO - Roleta Brasileira (Arquitetura Portável)")
    logger.info(f"Database: {Settings.DB_PATH}")
    logger.info("=" * 60)

    # OTIMIZAÇÃO: Pré-processa estratégias
    strategies_count = pre_process_strategies()
    logger.info(f"⚡ Otimização: {strategies_count} estratégias carregadas na memória")

    db = Database(str(Settings.DB_PATH))
    session_id = db.start_session()

    # Sistema de Relatórios e Analytics
    reporting = ReportingSystem(db)
    analytics.set_session(session_id)

    # New Agentic Memory
    memory_agent = MemoryAgent()

    metrics = Metrics(start_time=time.time())
    health_monitor = HealthMonitor(metrics)

    # Inicializa Monitor Visual (Abre o navegador)
    monitor = GameMonitor()

    bot = TelegramBot(Settings.TELEGRAM_TOKEN, Settings.TELEGRAM_CHAT_ID)
    strategy_state = StrategyState()
    context_filter = ContextFilter()
    turbulence_monitor = TurbulenceMonitor(bot)

    # Inicia Backup Automático e Listener de Comandos
    backup_system.start()
    bot.start_listener(reporting)

    # NOVAS REGRAS DE INTELIGÊNCIA
    wait_rounds = 0  # Contador de espera após WIN
    sequencia_greens = 0  # Contador de greens consecutivos

    # Histórico recente para análise de estabilidade longa (500)
    history_buffer = HistoryBuffer(max_size=500)
    transition_memory = TransitionMemory()

    try:
        if not monitor.start():
            logger.error("Falha ao iniciar monitor. Abortando sessão.")
            return False

        logger.info("Monitor iniciado. Aguardando detecção de números...")

        stats = db.get_statistics()
        logger.info(f"Estatísticas: {stats['total_numbers']} números salvos")

        last_heartbeat = time.time()

        while True:
            # Captura novo número (Utiliza MutationObserver no container estendido)
            numero_str = monitor.watch()
            if not numero_str:
                time.sleep(1)
                continue

            numero = int(numero_str)
            metrics.numbers_detected += 1
            metrics.last_number_time = time.time()
            logger.info(f"🔥 Novo Número Detectado: {numero}")

            # Atualiza histórico recente (mantém últimos 100 via FIFO)
            if not history_buffer.add(numero, time.time()):
                continue  # Ignora giro inconsistente (Windows 10 integrity)

            # 0. Atualiza memória de transições e detecta padrões (Somente após 60 giros)
            transition_memory.update(history_buffer.get_last(2))
            if len(history_buffer) >= Settings.STATS_WINDOW_SIZE:
                patterns = transition_memory.detect_pattern(numero)
                if patterns and numero in ESTRATEGIAS:
                    lines = "\n".join(
                        f"➡️ {n} ocorreu {x}x"
                        for n, x in sorted(
                            patterns.items(), key=lambda kv: kv[1], reverse=True
                        )[:2]
                    )
                    msg_pattern = (
                        f"📊 PADRÃO SEQUENCIAL DETECTADO\n\n"
                        f"Após o número {numero}:\n\n"
                        f"{lines}\n\n"
                        f"Possível repetição contextual."
                    )
                    bot.enviar(msg_pattern)

            # 1. Registro do número
            db.save_number(numero, telegram_sent=True, strategy=None)

            # 2. Notificação Imediata
            bot.enviar_imediato(f"🎲 Novo número: {numero}")

            # 3. Sticker Modo Espera se aguardando
            if wait_rounds > 0:
                bot.enviar_sticker_resultado(
                    "WIN", modo_espera=True
                )  # Passa modo_espera=True

            # 4. Redução de wait_rounds se houver
            can_search_strategy = True
            if wait_rounds > 0:
                logger.info(
                    f"⏳ Inteligência: Aguardando estabilidade ({wait_rounds} giros restantes)"
                )
                wait_rounds -= 1
                can_search_strategy = False

            # 5. Processamento de Estratégia Ativa
            if strategy_state.active:
                result = strategy_state.process_number(numero)

                if result in ["WIN_ENTRY", "WIN_PROTECTION"]:
                    metrics.green_count += 1
                    sequencia_greens += 1  # Incrementa sequência de greens
                    total_signals = metrics.green_count + metrics.red_count
                    accuracy = (
                        (metrics.green_count / total_signals) * 100
                        if total_signals > 0
                        else 0
                    )
                    win_type = "NA ENTRADA" if result == "WIN_ENTRY" else "NA PROTEÇÃO"

                    msg = (
                        f"🟢 WIN NO {numero} ({win_type})\n"
                        f"📊 PARTIDAS: 🟢 {metrics.green_count} | 🔴 {metrics.red_count}\n"
                        f"🎯 Taxa de acerto: {accuracy:.1f}%"
                    )
                    logger.info(f"WIN {win_type} detectado no {numero}")
                    bot.enviar_imediato(msg)

                    # Envia sticker baseado no resultado
                    gale_count = (
                        strategy_state.attempt - 1 if strategy_state.attempt > 0 else 0
                    )
                    bot.enviar_sticker_resultado("WIN", gale_count, sequencia_greens)

                    stats_msg = analytics.register(
                        strategy_state.strategy_id, result, strategy_name="Strategy"
                    )
                    if stats_msg:
                        bot.enviar(stats_msg)

                    # --- Analytics de Performance (Novo) ---
                    current_id = strategy_state.strategy_id
                    tracker.register_win(current_id)

                    # Update memory agent
                    result_type = "green" if result == "WIN_ENTRY" else "g1"
                    memory_agent.update_stats(numero, result_type)

                    # Alerta de HOT Strategy
                    winrate = tracker.should_notify(current_id)
                    if winrate:
                        msg_hot = (
                            "🔥 ESTRATÉGIA EM ALTA PERFORMANCE\n\n"
                            f"Estratégia Terminal:\nID: {current_id}\n\n"
                            f"📊 Assertividade:\n{winrate:.2f}%\n\n"
                            f"Base: {tracker.stats[current_id]['total']} operações"
                        )
                        bot.enviar(msg_hot)

                    strategy_state.reset()
                    # REGRA INTELIGENTE: Aguarda giros após WIN
                    wait_rounds = (
                        Settings.WAIT_ROUNDS_AFTER_ZERO
                        if numero == 0
                        else Settings.WAIT_ROUNDS_AFTER_WIN
                    )
                    logger.info(
                        f"✅ Inteligência: WIN no {numero}. Pausando por {wait_rounds} giros."
                    )

                elif result == "LOSS":
                    metrics.red_count += 1
                    sequencia_greens = 0  # Reseta sequência de greens
                    msg = f"🔴 LOSS CONFIRMADO\n❌ 3 proteções atingidas\nEncerrando leitura"
                    logger.info(f"LOSS detectado no {numero}")
                    bot.enviar_imediato(msg)

                    # Envia sticker RED
                    bot.enviar_sticker_resultado("LOSS")

                    stats_msg = analytics.register(
                        strategy_state.strategy_id, result, strategy_name="Strategy"
                    )
                    if stats_msg:
                        bot.enviar(stats_msg)

                    # --- Analytics de Performance (Novo) ---
                    tracker.register_loss(strategy_state.strategy_id)

                    # Update memory agent
                    memory_agent.update_stats(numero, "loss")

                    strategy_state.reset()
                    wait_rounds = 1  # No LOSS aguarda pelo menos 1

                elif result == "PROTECTION":
                    msg = (
                        f"⚠️ Proteção {strategy_state.attempt}/3\nSeguimos na estratégia"
                    )
                    logger.info(f"Proteção {strategy_state.attempt}/3 no {numero}")
                    bot.enviar(msg)
                    time.sleep(0.5)
                    continue

            # 6. Monitoramento de Contexto e Turbulência (Sempre ativo)
            has_turbulence, info = context_filter.should_block_entry(
                history_buffer.get_all(), numero
            )
            if info.get("type") not in ("initializing",) and has_turbulence:
                turbulence_monitor.update(has_turbulence, info)

            # 7. Verificação de Terminais Bagunçados
            history = history_buffer.get_all()
            if len(history) >= 6:
                last6 = history[-6:]
                terminals = [n % 10 for n in last6]
                if len(set(terminals)) == 6:  # Todos terminais diferentes
                    msg_baguncados = "🚨 Terminais baguncados na mesa!\nÚltimos 6 números com terminais totalmente diferentes."
                    bot.enviar_imediato(msg_baguncados)
                    bot.enviar_sticker(TERMINAIS_BAGUNCADOS_STICKER)
                    logger.info("Terminais baguncados detectados.")
                    wait_rounds = 2  # Pausa por 2 giros

            # 8. Busca nova estratégia (Modelo Alert-Only: Nunca Bloqueia)
            if not strategy_state.active and can_search_strategy:
                # SEMPRE busca estratégia, independente de warming_up ou turbulência
                signal = run_engine(history_buffer.get_all(), memory_agent, numero)
                if numero not in Settings.FORBIDDEN_NUMBERS and signal["strategy"]:
                    # LOG DE VALIDAÇÃO: Turbulência informativa não impede entrada
                    if has_turbulence and info.get("type") != "warming_up":
                        logger.info(
                            f"⚠️ Block ignorado por modo informativo de turbulência. Entrada para {numero} segue normalmente."
                        )

                    raw_strategy = signal["strategy"]
                    entry_targets = signal["entry_targets"]
                    protection_targets = signal["protection_targets"]
                    confidence = signal["confidence"]
                    reasoning = signal["reasoning"]

                    msg_completa = formatter.format_strategy_message(numero, {"raw": raw_strategy})
                    logger.info(
                        f"✅ Estratégia confirmada para {numero}. Confiança: {confidence}%"
                    )
                    logger.info(f"Razão: {reasoning}")
                    if bot.enviar(msg_completa):
                        strategy_state.activate(
                            numero, numero, entry_targets, protection_targets
                        )
                    else:
                        logger.warning(
                            f"❌ FALHA no envio da entrada para {numero}. Telegram rejeitou."
                        )
                else:
                    # LOG: Motivo exato de não enviar entrada
                    if numero in Settings.FORBIDDEN_NUMBERS:
                        logger.debug(
                            f"🚫 Número {numero} está na lista FORBIDDEN_NUMBERS. Sem estratégia."
                        )
                    else:
                        logger.debug(
                            f"📭 Sem estratégia registrada para o número {numero}."
                        )

            if time.time() - last_heartbeat > 60:
                logger.info("Heartbeat: Sistema ativo")
                last_heartbeat = time.time()

            time.sleep(0.5)

    except Exception as e:
        logger.error(f"Erro na execução da sessão: {e}", exc_info=True)
        return False  # Indica que a sessão caiu por erro
    finally:
        db.end_session(session_id, metrics.numbers_detected, metrics.errors_count)
        monitor.stop()


def main():
    """Loop de resiliência (Auto-Restart)"""
    max_restarts = 10
    restart_count = 0

    while restart_count < max_restarts:
        try:
            success = run_bot()
            if success is False:
                restart_count += 1
                wait_time = min(60, 5 * restart_count)
                logger.warning(
                    f"Sessão encerrada com erro. Reiniciando em {wait_time}s ({restart_count}/{max_restarts})..."
                )
                time.sleep(wait_time)
            else:
                # Se run_bot retornar None ou True (saída limpa), podemos decidir se reiniciamos
                break
        except KeyboardInterrupt:
            logger.warning("Encerrando bot via teclado.")
            # Quando parado manualmente, tenta enviar o relatório final
            try:
                db = Database(str(Settings.DB_PATH))
                reporting = ReportingSystem(db)
                bot = TelegramBot(Settings.TELEGRAM_TOKEN, Settings.TELEGRAM_CHAT_ID)

                logger.info("Enviando relatório de encerramento...")
                relatorio = reporting.get_weekly_report(clean=True)
                bot.enviar(relatorio)
            except:
                pass
            break
        except Exception as fatal_e:
            logger.critical(f"Erro fatal não tratado: {fatal_e}")
            break


if __name__ == "__main__":
    main()

