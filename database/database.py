import sqlite3
import time
from enum import Enum

connection = sqlite3.connect('tictactoe.db')
cursor = connection.cursor()


class Stat(Enum):
    """Stats enum for the database."""

    TOTAL_COMMANDS = ['UPDATE stats SET total_commands=? WHERE id=?', 'SELECT total_commands FROM stats WHERE id=?']
    START_COMMAND = ['UPDATE stats SET start_command=? WHERE id=?', 'SELECT start_command FROM stats WHERE id=?']
    HELP_COMMAND = ['UPDATE stats SET help_command=? WHERE id=?', 'SELECT help_command FROM stats WHERE id=?']
    STOP_COMMAND = ['UPDATE stats SET stop_command=? WHERE id=?', 'SELECT stop_command FROM stats WHERE id=?']
    TOTAL_GAMES = ['UPDATE stats SET total_games=? WHERE id=?', 'SELECT total_games FROM stats WHERE id=?']


def create_tables():
    """Create the table for the stats."""
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stats(
        id date PRIMARY KEY,
        total_commands integer,
        start_command integer,
        help_command integer,
        stop_command integer,
        total_games integer
        )
        """
    )
    connection.commit()


def update_stat(stat: Stat):
    """Update the given stat by 1 in the database for the current date.
    :param stat: The stat
    """
    current_date = get_current_date()
    if not current_date_exists():
        cursor.execute("""
        INSERT INTO stats(id, total_commands, start_command, help_command, stop_command, total_games)
        VALUES (?, 0, 0, 0, 0, 0)""", [current_date])
        connection.commit()
    queries = stat.value
    cursor.execute(queries[1], [current_date])
    result = cursor.fetchall()[0][0]
    result += 1
    cursor.execute(queries[0], [result, current_date])
    connection.commit()


def current_date_exists() -> bool:
    """Check if the current date is already in the database.

    :return: True if the date exists in the database, otherwise False.
    """
    cursor.execute('SELECT id FROM stats WHERE id=?', [get_current_date()])
    result = cursor.fetchall()
    if not result:
        return False
    else:
        return True


def get_current_date() -> str:
    """Returns the current date for in the database.

    :return: time string
    """
    return time.strftime('%Y-%m-%d', time.localtime())


def get_stats(cur=cursor) -> dict:
    """Returns the summed stats in a dict.

    :param cur: The database cursor that the function has to use.
    :return: Dict with all the bot stats.
    """
    cur.execute('SELECT sum(total_commands), '
                'sum(start_command), '
                'sum(help_command), '
                'sum(stop_command), '
                'sum(total_games) FROM stats')
    result = cur.fetchall()[0]
    return {
        'total_commands': result[0],
        'start_command': result[1],
        'help_command': result[2],
        'stop_command': result[3],
        'total_games': result[4]
    }


def disconnect_database():
    """Close the database cursor and connection."""
    cursor.close()
    connection.close()
