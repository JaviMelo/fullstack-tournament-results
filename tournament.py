#!/usr/bin/env python

# tournament.py -- implementation of a Swiss-system tournament
# This file defines multiple Python functions to be used in facilitating
# a Swiss-system tournament

import psycopg2


# Connect to PostgreSQL database:

def connect():
    return psycopg2.connect("dbname=tournament")


# Remove all the records from a tournament:

def deleteMatches(tournament='blnk'):
    db = connect()
    db_cursor = db.cursor()
    if tournament == 'blnk':
        query = "DELETE FROM matches"
        db_cursor.execute(query)
        print '==>  All matches were deleted successfully.'
    else:
        query = "DELETE FROM matches WHERE tournament = %s"
        db_cursor.execute(query, (tournament,))
        print '==>  All matches were deleted from '
        + tournament + 'successfully.'
    db.commit()
    db.close()


# Removes players from the database:

def deletePlayers(playerID='blnk'):
    db = connect()
    db_cursor = db.cursor()
    if playerID == 'blnk':
        query = "DELETE FROM players where id <> 0"
        db_cursor.execute(query)
        print '==>  All players were deleted successfully.'
    else:
        query = "DELETE FROM players WHERE id = %s"
        db_cursor.execute(query, (playerID))
        print '==>  Player ID: ' + playerID + ' deleted.'
    db.commit()
    db.close()


# Return the number of player registered:

def countPlayers(tournament='blnk'):
    db = connect()
    db_cursor = db.cursor()
    if tournament == 'blnk':
        query = "SELECT count(*) FROM players WHERE id <> 0"
        db_cursor.execute(query)
        rows = db_cursor.fetchone()
        print '==>  ' + str(rows[0]) + ' players are registered for'
        'all tournaments.'
    else:
        query = "SELECT count(*) FROM players WHERE tournament = %s AND id <> 0"
        db_cursor.execute(query, (tournament,))
        rows = db_cursor.fetchone()
        print '==>  ' + str(rows[0]) + ' players are registered'
        'for tournament + tournament + '
    db.commit()
    db.close()
    return rows[0]


# Add a player to the tournament database:

def registerPlayer(tournament, name):
    db = connect()
    db_cursor = db.cursor()
    query = "INSERT INTO players (tournament, name) VALUES (%s, %s)"
    # Try to register player 100 times. In case serial generated id
    # == previously entered user id
    for i in range(1, 100):
        try:
            db_cursor.execute(query, (tournament, name,))
            break
        except psycopg2.IntegrityError:
            # If error from duplicate id is thrown, roll back changes.
            db.rollback()
    else:
        print 'We tried 100 times to enter register the player and a unique'
        'id could not be assigned.  Run registerPlayer(tournament) again to'
        'try 100 more times.'
    print '==>  ' + name + ' has been registered for tournament: ' + tournament
    db.commit()
    db.close()


def playerStandings():
    db = connect()
    db_cursor = db.cursor()
    db_cursor.execute("SELECT * FROM playerStandings")
    standings = db_cursor.fetchall()
    db.close()
    print '==>  Player standings compiled successfully.'
    return standings


# Record the result of a single match between 2 players:

def reportMatch(tournament, playerID, opponent, result):
    db = connect()
    db_cursor = db.cursor()
    query = "INSERT INTO matches (tournament, player_id, opponent_id, result)"
    "VALUES (%s, %s, %s, %s)"
    db_cursor.execute(query, (tournament, playerID, opponent, result))
    print '==>  Match recorded successfully. \n ====>  Player ID: %s \n ====>'
    'Opponent ID: %s \n ====>  Tournament: %s \n ====>  Result: %s' % (str(playerID), str(opponent), tournament, result)
    if opponent != 0:
        if result == 'win':
            db_cursor.execute(query, (tournament, opponent, playerID, 'lose'))
            print '==>  Match recorded successfully. \n ====>'
            'Player ID: %s \n ====>  Opponent ID: %s \n ====>'
            'Tournament: %s \n ====>  Result: lose' % (str(opponent), str(playerID), tournament)
        elif result == 'lose':
            print '==>  Match recorded successfully. \n ====>'
            'Player ID: %s \n ====>  Opponent ID: %s \n ====>'
            'Tournament: %s \n ====>  Result: win' % (str(opponent), str(playerID), tournament)
            db_cursor.execute(query, (tournament, opponent, playerID, 'win'))
        else:
            db_cursor.execute(query, (tournament, opponent, playerID, 'tie'))
            print '==>  Match recorded successfully. \n ====>'
            'Player ID: %s \n ====>  Opponent ID: %s \n ====>'
            'Tournament: %s \n ====>  Result: tie' % (str(opponent), str(playerID), tournament)
    db.commit()
    db.close()


# Returns a list of pairs of players for the next round of a match:

def swissPairings(tournament='blnk'):
    db = connect()
    db_cursor = db.cursor()
    getPlayers = "SELECT id, name FROM v_standings"
    fromTournament = " WHERE tournament = %s"
    if tournament == 'blnk':
        db_cursor.execute(getPlayers)
    else:
        db_cursor.execute(getPlayers + fromTournament, (tournament,))
    players = db_cursor.fetchall()
    swissPairs = []
    alreadyPlayed = []
    recordBye = []
    countOfPlayers = len(players)
    # Assign a bye week if there is an odd number of players in the round
    if countOfPlayers % 2:
        playersByLeastWins = """
        SELECT v_standings.id AS id, v_standings.name AS name
        FROM v_standings
        ORDER BY v_standings.wins, v_standings.omw
        """
        db_cursor.execute(playersByLeastWins)
        playersByLeastWins = db_cursor.fetchall()
        playersAlreadyBye = """
        SELECT player_id AS id, player_name AS name
        FROM v_results
        WHERE opponent_id=0
        GROUP BY player_id, player_name
        """
        db_cursor.execute(playersAlreadyBye)
        playersAlreadyBye = db_cursor.fetchall()
        byeCandidates = [player for player in playersByLeastWins
                         if player not in playersAlreadyBye]
        playerWithBye = [byeCandidates[0], ]
        players = [player for player in players if player not in playerWithBye]
        recordBye = (byeCandidates[0][0], byeCandidates[0][1], 0, 'BYE')
    # Pair players based on the stipulations in the doc string
    while countOfPlayers > 1:
        player = players[0]
        findOpponents = """
            SELECT waldo.id, waldo.name
            FROM (
                SELECT v_standings.*, oppid.played
                FROM v_standings LEFT OUTER JOIN (
                    SELECT v_results.opponent_id AS played
                    FROM v_results
                    WHERE v_results.player_id = %s
                    GROUP BY v_results.opponent_id) AS oppid
                ON v_standings.id = oppid.played) AS waldo
            WHERE waldo.played IS NULL AND waldo.id <> %s
            """
        withTournament = " AND waldo.tournament =%s"
        byeInEffect = " AND waldo.id <> %s"
        if tournament == 'blnk':
            if recordBye == []:
                db_cursor.execute(findOpponents,
                                  str(player[0]), str(player[0]))
            else:
                db_cursor.execute(findOpponents + byeInEffect,
                                  str(player[0]), str(player[0]),
                                  str(playerWithBye[0][0]))
        else:
            if recordBye == []:
                db_cursor.execute(findOpponents + withTournament,
                                  str(player[0]), str(player[0]), tournament)
            else:
                db_cursor.execute(findOpponents + withTournament + byeInEffect,
                                  str(player[0]), str(player[0]), tournament,
                                  str(playerWithBye[0][0]))

        opponentList = db_cursor.fetchall()
        opponentList = [opponent for opponent in opponentList
                        if opponent not in alreadyPlayed]
        try:
            opponent = opponentList[0]
            match = player + opponent
            swissPairs += (match,)
            alreadyPlayed += (player, opponent)
            players = [x for x in players if x not in (player, opponent)]
            countOfPlayers = len(players)
        except:
            print str(player) + ' has played all opponents in Tournament: '
            + tournament
            print 'Aborting swissPairings().'
            break
    db.rollback()
    db.close()
    recordBye = [recordBye, ]
    for pair in swissPairs:
        print '==> ' + str(pair)
    if recordBye == [[]]:
        return swissPairs
    else:
        print '==> ' + str(recordBye)
        return recordBye + swissPairs