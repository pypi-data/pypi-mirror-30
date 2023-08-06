"""Provide UV index reporting capabilities to Le bot."""


from contextlib import contextmanager
from datetime import time
from logging import getLogger

import requests
from telegram.ext import CommandHandler
from telegram.ext.jobqueue import Days


logger = getLogger()

places = {
    'antartica': 'ANT&Aacute;RTICA',
    'antofagasta': 'ANTOFAGASTA',
    'arica': 'ARICA (UNIVERSIDAD DE TARAPAC&Aacute;)',
    'caldera': 'CALDERA',
    'concepcion': 'CONCEPCI&Oacute;N',
    'cordillera_rm': 'CORDILLERA REGI&Oacute;N METROPOLITANA',
    'coyhaique': 'COYHAIQUE',
    'tololo': 'EL TOLOLO',
    'iquique': 'IQUIQUE',
    'isla_pascua': 'ISLA DE PASCUA',
    'serena': 'LA SERENA',
    'litoral_central': 'LITORAL CENTRAL',
    'pmontt': 'PUERTO MONTT',
    'parenas': 'PUNTA ARENAS',
    'rancagua': 'RANCAGUA',
    'san_pedro': 'SAN PEDRO DE ATACAMA',
    'santiago': 'SANTIAGO',
    'talca': 'TALCA (UNIVERSIDAD AUTONOMA)',
    'temuco': 'TEMUCO (UNIVERSIDAD CAT&Oacute;LICA DE TEMUCO)',
    'chillan': 'TERMAS DE CHILL&Aacute;N',
    'valdivia': 'VALDIVIA',
}

place_ids = places.keys()
comma_sep_place_ids = ', '.join(place_ids)
valid_places_msg_fragment = 'Valid places are: {}.'.format(comma_sep_place_ids)


@contextmanager
def handle_unhandled_exceptions(bot, chat_id):
    """Handle unhandled exceptions."""
    try:
        yield

    except Exception:
        logger.exception('Unhandled exception!')
        bot.sendMessage(chat_id=chat_id, text='Something went wrong!')


def print_uv_index(bot, chat_id, place):
    """Print the UV index corresponding to ``place``."""
    try:
        response = requests.get(
            'http://archivos.meteochile.gob.cl/portaldmc/meteochile/js/'
            'indice_radiacion.json'
        )

        data = response.json()
        radiation_data = data['RadiacionUVB']

        radiation_stgo = next(
            filter(lambda p: p['nombre'] == places[place], radiation_data)
        )

        date = radiation_stgo['fechapron']
        index = radiation_stgo['indicepron'].split(':')

        text = 'Pronostico Dia: {}. UV index: {}({})'.format(
            date, index[0], index[1])

        bot.sendMessage(chat_id=chat_id, text=text)

    except KeyError:
        if place not in places:
            error_message_template = (
                '{place} is not a valid place. {valid_places_msg_fragment}')

            error_message = error_message_template.format(
                place=place,
                valid_places_msg_fragment=valid_places_msg_fragment
            )

            bot.sendMessage(chat_id=chat_id, text=error_message)

        else:
            raise


def get_uv_index(bot, update, args):
    """Parse args to extract a place and print the place's uv index."""
    with handle_unhandled_exceptions(bot, update.message.chat_id):
        try:
            print_uv_index(bot, update.message.chat_id, args[0])

        except IndexError:
            if len(args) < 1:
                place_ids = places.keys()
                comma_sep_ids = ', '.join(place_ids)

                error_message_template = (
                    'You have to specify a place. Valid places are: {}.')

                error_message = error_message_template.format(comma_sep_ids)

                bot.sendMessage(
                    chat_id=update.message.chat_id, text=error_message)

            else:
                raise


def callback_uv_index(bot, job):
    """Print UV index for the corresponding job context.

    ``job.context`` shoud be a tuple of the form: ``(chat_id, place)``
    """
    print_uv_index(bot, *job.context)


def start_uv_index(bot, update, job_queue, args):
    """Schedule a calls to ``callback_uv_index``."""
    with handle_unhandled_exceptions(bot, update.message.chat_id):
        try:
            hour = int(args[0])
            minute = int(args[1])
            place = args[2]

            if place not in places:
                raise InvalidPlace

            job_queue.run_daily(
                callback_uv_index,
                time=time(hour, minute),
                days=(Days.MON, Days.TUE, Days.WED, Days.THU, Days.FRI),
                context=(update.message.chat_id, place),
                name='UV Index Daily Report'
            )

            bot.sendMessage(
                chat_id=update.message.chat_id,
                text='Initiating UV Index daily report.'
            )

        except IndexError:
            if len(args) is not 3:
                error_message_template = (
                    'You have to pass the hour, minute and place in the '
                    'format: 12 59 santiago. {valid_places_msg_fragment}'
                )

                error_message = error_message_template.format(
                    valid_places_msg_fragment=valid_places_msg_fragment)

                bot.sendMessage(
                    chat_id=update.message.chat_id, text=error_message)

            else:
                raise

        except InvalidPlace:
            error_message_template = (
                'You entered an invalid place. {valid_places_msg_fragment}'
            )

            error_message = error_message_template.format(
                valid_places_msg_fragment=valid_places_msg_fragment)

            bot.sendMessage(
                chat_id=update.message.chat_id, text=error_message)

        except ValueError as ve:
            if 'invalid literal for int' in str(ve):
                text = (
                    'You seem to have entered a wrong integer number. Check '
                    'that you are passing well formatted integers and that '
                    'the parameters in the correct order (hour, minute, '
                    'place).'
                )

                bot.send_message(update.message.chat_id, text)

            else:
                raise


def stop_uv_index(bot, update, job_queue):
    """Stop an UV index report job."""
    with handle_unhandled_exceptions(bot, update.message.chat_id):
        for j in job_queue.jobs():
            if j.name == 'UV Index Daily Report' and \
                    j.context[0] == update.message.chat_id:
                j.schedule_removal()

        bot.sendMessage(
            chat_id=update.message.chat_id,
            text='Canceled all UV Index daily reports.'
        )


send_handler = CommandHandler('uvindex', get_uv_index, pass_args=True)


start_handler = CommandHandler(
    'start_uvindex', start_uv_index, pass_args=True, pass_job_queue=True)


stop_handler = CommandHandler(
    'stop_uvindex', stop_uv_index, pass_job_queue=True)


class InvalidPlace(ValueError):
    """Raise when the user enters an invalid place."""

    def __init__(self, info=None):
        """Initialize the error."""
        message = 'An invalid place was passed.'
        super().__init__(message + ' ' + info if info else message)
