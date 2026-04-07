import time
import os
from datetime import datetime
from config.settings import Settings

# --- MODO PLAYTECH WEBSOCKET ---
from core.playtech_ws import PlaytechMonitor
from analytics.context_filter import ContextFilter
from analytics.strategy_performance import tracker
from utils.history_buffer import HistoryBuffer
from utils.turbulence_monitor import TurbulenceMonitor
# -------------------------------

from services.bot import TelegramBot
from engine import gerar_mensagem_por_numero, StrategyState, pre_process_strategies, get_optimized_strategy, ESTRATEGIAS
from engine.parser import parse_strategy_targets, parse_protection_targets
from utils.logger import setup_logger
from analytics.metrics import Metrics, HealthMonitor
from storage.database import Database
from services.reporting import ReportingSystem
from analytics.strategy_analytics import analytics
from storage.backup import backup_system

import requests

# Settings are automatically loaded by the Settings class

logger = setup_logger('main_playtech')

def send_signal_to_bridge(number, strategy, confidence, entry_targets, protection_targets):
    """Envia sinal para o frontend Vision Pro"""
    bridge_url = "http://localhost:4000/api/webhook/signal"
    
    payload = {
        "number": number,
        "strategy": strategy,
        "confidence": confidence,
        "entry": entry_targets,
        "protection": protection_targets
    }
    
    try:
        response = requests.post(bridge_url, json=payload, timeout=0.5)
        print(f"Vision Pro signal sent: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar sinal para Vision Pro: {e}")
        return False

def main():

    logger.info("="*60)
    logger.info("BOT INICIADO - Roleta Brasileira (Playtech WebSocket)")
    logger.info("Modo: Interceptação Socket.IO / WS")
    logger.info("🗣️ VOICE DISABLED - 100% Visual Dashboard")
    logger.info("="*60)

    # OTIMIZAÇÃO: Pré-processa estratégias
    strategies_count = pre_process_strategies()
    logger.info(f"⚡ Otimização: {strategies_count} estratégias carregadas na memória")

    db = Database(str(Settings.DB_PATH))
    session_id = db.start_session()

    # Sistema de Relatórios e Analytics
    reporting = ReportingSystem(db)
    analytics.set_session(session_id)

    metrics = Metrics(start_time=time.time())
    health_monitor = HealthMonitor(metrics)

    # Inicializa Monitor Playtech
    monitor = PlaytechMonitor()
    
    bot = TelegramBot(Settings.TELEGRAM_TOKEN, Settings.TELEGRAM_CHAT_ID)
    strategy_state = StrategyState()
    context_filter = ContextFilter()
    turbulence_monitor = TurbulenceMonitor(bot)

    # Inicia Backup Automático e Listener de Comandos
    backup_system.start()
    bot.start_listener(reporting)

    # Estado local para evitar processar o mesmo número repetidamente no loop While
    last_process_token = None
    
    # NOVAS REGRAS DE INTELIGÊNCIA
    wait_rounds = 0  # Contador de espera após WIN
    STICKER_TUBULENCIA = "CAACAgEAAxkBAAEQgLNpjqgYIAkuLWqX_v-suGpSThI-SgACBQYAAmTxwEej7Igzpi1WZDoE"
    
    # Histórico recente para análise de estabilidade longa (50-100)
    history_buffer = HistoryBuffer(max_size=100)

    try:
        monitor.start()

        # Blocos de instrução manual não necessários (WS é automático)
        logger.info("Monitor iniciado. Aguardando pacotes do socket...")
        
        stats = db.get_statistics()
        logger.info(f"Estatísticas: {stats['total_numbers']} números")

        loop_count = 0
        last_heartbeat = time.time()
        
        while True:
            # Pega o último número conhecido pelo socket (agora retorna dicio com token)
            data_socket = monitor.watch()
            numero_atual_socket = data_socket.get("number")
            token_atual = data_socket.get("token")

            # Só processa se for um número válido E se for um token NOVO
            if numero_atual_socket and token_atual != last_process_token:
                last_process_token = token_atual # Marca como processado
                
                # INÍCIO DO PIPELINE DE PROCESSAMENTO
                metrics.numbers_detected += 1
                metrics.last_number_time = time.time()
                mensagem = f"🔥 Novo Número Detectado (WS): {numero_atual_socket} (Token: {token_atual})"
                logger.info(mensagem)
                logger.info(f"SILENCED_VOICE: {mensagem}")
                
                numero = int(numero_atual_socket) # Converte para int

                # --- HARD FILTER DISABLED (Todos os números agora são processados) ---
                # if numero in [0, 8, 11, 17, 22, 27, 33]:
                #     logger.warning(f"⛔ HARD FILTER: Número {numero} detectado e IGNORADO.")
                #     continue
                # ----------------------------------------------------------------------
                
                # Atualiza histórico recente (mantém últimos 100 via FIFO)
                history_buffer.add(numero)
                
                # 3. Registro do número
                db.save_number(numero, telegram_sent=True, strategy=None)
                
                # 2. Notificação Imediata
                bot.enviar_imediato(f"🎲 Novo número: {numero}")

                # 4. Redução de wait_rounds se houver
                can_search_strategy = True
                if wait_rounds > 0:
                    logger.info(f"⏳ Inteligência: Aguardando estabilidade ({wait_rounds} giros restantes)")
                    wait_rounds -= 1
                    can_search_strategy = False

                if strategy_state.active:
                    # Verifica resultado da estratégia ativa
                    result = strategy_state.process_number(numero)
                    
                    if result == "WIN_ENTRY" or result == "WIN_PROTECTION":
                        metrics.green_count += 1
                        total_signals = metrics.green_count + metrics.red_count
                        accuracy = (metrics.green_count / total_signals) * 100 if total_signals > 0 else 0
                        win_type = "NA ENTRADA" if result == "WIN_ENTRY" else "NA PROTEÇÃO"
                        
                        msg = (
                            f"🟢 WIN NO {numero} ({win_type})\n"
                            f"📊 PARTIDAS: 🟢 {metrics.green_count} | 🔴 {metrics.red_count}\n"
                            f"🎯 Taxa de acerto: {accuracy:.1f}%"
                        )
                        mensagem = f"WIN {win_type} detectado no {numero}"
                        logger.info(mensagem)
                        logger.info(f"SILENCED_VOICE: {mensagem}")
                        bot.enviar_imediato(msg)
                        
                        # Captura e envia o box de analytics detalhado
                        stats_msg = analytics.register(strategy_state.strategy_id, result, strategy_name="Strategy")
                        if stats_msg:
                            bot.enviar(stats_msg)
                            
                        # --- Analytics de Performance (Novo) ---
                        current_id = strategy_state.strategy_id
                        tracker.register_win(current_id)
                        
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
                        # ----------------------------------------
                            
                        strategy_state.reset()
                        # REGRA INTELIGENTE: Aguarda giros após WIN
                        wait_rounds = Settings.WAIT_ROUNDS_AFTER_ZERO if numero == 0 else Settings.WAIT_ROUNDS_AFTER_WIN
                        mensagem = f"✅ Inteligência: WIN no {numero}. Pausando por {wait_rounds} giros."
                        logger.info(mensagem)
                        logger.info(f"SILENCED_VOICE: {mensagem}")
                        
                    elif result == "LOSS":
                        metrics.red_count += 1
                        msg = f"🔴 LOSS CONFIRMADO\n❌ 3 proteções atingidas\nEncerrando leitura"
                        mensagem = f"LOSS detectado no {numero}"
                        logger.info(mensagem)
                        logger.info(f"SILENCED_VOICE: {mensagem}")
                        bot.enviar_imediato(msg)
                        
                        # Captura e envia o box de analytics detalhado
                        stats_msg = analytics.register(strategy_state.strategy_id, result, strategy_name="Strategy")
                        if stats_msg:
                            bot.enviar(stats_msg)
                            
                        # --- Analytics de Performance (Novo) ---
                        tracker.register_loss(strategy_state.strategy_id)
                        # ----------------------------------------
                            
                        strategy_state.reset()
                        # No LOSS também permitimos re-entrada se o número for base de algo
                        wait_rounds = 1
                        
                    elif result == "PROTECTION":
                        msg = f"⚠️ Proteção {strategy_state.attempt}/3\nSeguimos na estratégia"
                        mensagem = f"Proteção {strategy_state.attempt}/3 no {numero}"
                        logger.info(mensagem)
                        logger.info(f"SILENCED_VOICE: {mensagem}")
                        success = bot.enviar(msg)
                        continue
                
                # 6. Monitoramento de Contexto e Turbulência (Sempre ativo)
                has_turbulence, info = context_filter.should_block_entry(history_buffer.get_all(), numero)
                if info.get("type") not in ("initializing",) and has_turbulence:
                    turbulence_monitor.update(has_turbulence, info)

                # 7. Busca nova estratégia (Modelo Alert-Only: Nunca Bloqueia)
                if not strategy_state.active and can_search_strategy:
                    # SEMPRE busca estratégia, independente de warming_up ou turbulência
                    opt_data = get_optimized_strategy(numero)
                    if opt_data:
                        raw_strategy = opt_data['raw']
                        entry_targets = opt_data['entry']
                        protection_targets = opt_data['protection']
                        
                        time_now = datetime.now().strftime("%H:%M")
                        
                        # Send to Vision Pro dashboard
                        send_signal_to_bridge(
                            numero, 
                            raw_strategy['leitura'], 
                            0.85, 
                            entry_targets, 
                            protection_targets
                        )
                        
                        msg_completa = (

                            "🍀Entrada Confirmada🍀\n"
                            f"🕒 {time_now}\n"
                            f"📍 Número base: {numero}\n\n"
                            f"🎯 Entrada:\n{raw_strategy['entrada']}\n\n"
                            f"🛡️ Proteção:\n{raw_strategy.get('cobertura', '')}\n\n"
                            f"🧠 Leitura: {raw_strategy['leitura']}\n\n"
                            "⏱️ Gestão:\nAté 3 proteções.\nSem insistência."
                        )
                        logger.info(f"✅ Estratégia confirmada para {numero}.")
                        if bot.enviar(msg_completa):
                            strategy_state.activate(numero, numero, entry_targets, protection_targets)
                # FIM DO PIPELINE

            else:
                loop_count += 1
                
                # Relatórios periódicos automáticos podem ser adicionados aqui se necessário

                if time.time() - last_heartbeat > 30:
                    logger.info(f"Sync: Aguardando dados... (Loop {loop_count})")
                    last_heartbeat = time.time()

            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.warning("Parando bot pelo teclado (Ctrl+C)...")
        try:
            logger.info("Enviando relatório de encerramento...")
            relatorio = reporting.get_weekly_report(clean=True)
            bot.enviar(relatorio)
        except Exception as report_err:
            logger.error(f"Erro ao enviar relatório de encerramento: {report_err}")
            
    except Exception as e:
        logger.critical(f"Erro Fatal: {e}", exc_info=True)
    finally:
        db.end_session(session_id, metrics.numbers_detected, metrics.errors_count)
        monitor.stop()

if __name__ == "__main__":
    main()

