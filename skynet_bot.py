import time
import signal
from typing import List

from core.skynet_capture import LiveCapture
from core.bet_executor import BetExecutor
from engine.decision_engine import DecisionEngine
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger('skynet')

RUNNING = True


def signal_handler(sig, frame):
    global RUNNING
    logger.info('Recebido sinal de encerramento. Finalizando...')
    RUNNING = False


def build_history_buffer(history: List[int], incoming_number: int, max_size: int = 30) -> List[int]:
    history.append(incoming_number)
    if len(history) > max_size:
        history.pop(0)
    return history


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    url = Settings.GAME_URL or 'https://game.playtech.com/live/roulette'
    logger.info(f'Iniciando SkynetChat LiveBot em: {url}')

    capture = LiveCapture(url=url, headless=Settings.HEADLESS)
    engine = DecisionEngine(db_path=str(Settings.DATA_DIR / 'live_bot.db'))

    history = []
    bet_executor = None

    if not capture.start():
        logger.error('Falha ao iniciar LiveCapture. Abortando.')
        return

    try:
        # Prepara executor se for página aberta localmente (o mesmo page é utilizado)
        if capture.page:
            bet_executor = BetExecutor(capture.page)

        while RUNNING:
            number = capture.get_latest_number()
            if number is None:
                time.sleep(0.001)
                continue

            history = build_history_buffer(history, number)
            color = engine.number_color(number)
            bet_size = engine.martingale_modificada(history)
            strategy_text = 'martingale_modificada'
            logger.info(f'🎯 NÚMERO: {number} | COR: {color} | APOSTA: {bet_size}')

            engine.log_bet(number=number, color=color, strategy=strategy_text, bet_size=bet_size)

            if bet_executor is not None:
                try:
                    bet_executor.click_bet(number, amount=bet_size)
                    logger.info('✅ Aposta executada por BetExecutor')
                except Exception as ex:
                    logger.warning(f'💥 Falha ao executar aposta: {ex}')

            # Evita loop super agressivo (garante <5ms por ciclo em geral)
            time.sleep(0.003)

    except Exception as exc:
        logger.error(f'Erro no loop principal Skynet: {exc}', exc_info=True)

    finally:
        capture.stop()
        engine.close()


if __name__ == '__main__':
    main()
