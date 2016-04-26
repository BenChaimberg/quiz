#!/usr/bin/python

from random import randint
import os


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    return None


class TimeoutError(Exception):
    def __init__(self):
        pass


class FailError(Exception):
    def __init__(self):
        pass


class TeamRangeError(Exception):
    def __init__(self):
        pass


class EvenTeamError(Exception):
    def __init__(self):
        pass


class RoundsError(Exception):
    def __init__(self):
        pass


class MatchError(Exception):
    def __init__(self, rank, re_num, re_num_big):
        self.rank = rank
        self.re_num = re_num
        self.re_num_big = re_num_big


class Team:
    def __init__(self, name):
        self.name = name
        self.diff = 0
        self.wins = 0
        self.losses = 0
        self.rooms = []
        self.opps = []


class Matchup:
    def __init__(self, team1, team2):
        self.teams = [team1, team2]
        self.room = None
        self.rooms = []
        for i in range(1, NUM_ROOMS+1):
            self.rooms.append(str(i))
        for i in self.teams:
            for j in i.rooms:
                if ALLOW_TWO_ROOMS is True:
                    once = []
                    for k in self.rooms:
                        if str(j) == str(k):
                            if str(j) in once:
                                self.rooms.remove(str(j))
                            else:
                                once.append(j)
                else:
                    for k in self.rooms:
                        if str(j) == str(k):
                            self.rooms.remove(str(j))


def inputs():
    global NUM_TEAMS
    global NUM_ROOMS
    global NUM_ROUNDS
    while True:
        try:
            NUM_TEAMS = int(raw_input(
                'How many teams in the tournament? Press enter for 32. '
            ) or 32)
            if NUM_TEAMS < 16 or NUM_TEAMS > 32:
                raise TeamRangeError
            if NUM_TEAMS % 2 == 1:
                raise EvenTeamError
            break
        except ValueError:
            print 'That wasn\'t a number, try again!'
        except TeamRangeError:
            print 'Number of teams must be between 16 and 32, try again!'
        except EvenTeamError:
            print 'Number of teams must be even, try again!'
    NUM_ROOMS = NUM_TEAMS/2
    while True:
        try:
            NUM_ROUNDS = int(raw_input(
                'How many rounds in the tournament? Press enter for 10. '
            ) or 10)
            if NUM_ROUNDS + 1 > NUM_TEAMS:
                raise RoundsError
            break
        except ValueError:
            print 'That wasn\'t a number, try again!'
        except RoundsError:
            print 'Too many rounds, try again!'
    teams = []
    for i in range(1, NUM_TEAMS+1):
        name = str(raw_input(''.join(str(x) for x in [
            'Team ',
            i,
            ' name. Press enter for generic names. '
        ])) or ''.join(str(x) for x in ['Team ', i]))
        team = Team(name)
        teams.append(team)
    return teams


def rank(teams):
    ranking = [teams[0]]
    for i in teams:
        for j in ranking:
            if i.diff < j.diff:
                ranking.insert(ranking.index(j), i)
                break
        if i not in ranking:
            ranking.append(i)
    for i in ranking:
        i.rank = ranking.index(i)
    return ranking


def init_matchups(teams, re_index, re_num, re_num_big):
    ranking_perm = rank(teams)
    ranking = rank(teams)
    matchups = []
    while not ranking == []:
        possibles = []
        matchups_len = len(matchups)
        i = ranking.pop(0)
        index = 0
        if i.rank == re_index:
            index += re_num
        for j in ranking:
            if ranking.index(j) < index:
                continue
            possibles.append(j)
            if ALLOW_TWO_OPPS is True:
                once = []
                for k in i.opps:
                    if j == k:
                        if j in once:
                            possibles.remove(j)
                        else:
                            once.append(j)
            else:
                for k in i.opps:
                    if j == k:
                        possibles.remove(j)
        for j in possibles:
            matchup = Matchup(i, j)
            if not matchup.rooms == []:
                ranking.remove(j)
                matchups.append(matchup)
                break
        if matchups_len == len(matchups):
            re_num += 1
            re_num_big = 1
            if re_num_big >= len(matchups):
                raise FailError
            if re_num >= (
                len(ranking_perm)
                - ranking_perm.index(matchups[-1*re_num_big].teams[0])
                - 1
            ) or re_num == -1:
                re_num = 1
                re_num_big += 1
            if re_num_big >= len(matchups):
                raise FailError
            re_rank_next = matchups[-1*re_num_big].teams[0].rank
            raise MatchError(re_rank_next, re_num, re_num_big)
    return matchups


def make_rooms(matchups, index, try_num):
    unused_rooms = []
    continued = False
    for i in range(1, NUM_ROOMS+1):
        unused_rooms.append(str(i))
    for i in matchups:
        for j in i.rooms:
            if str(j) in unused_rooms:
                check = (
                    NUM_ROOMS
                    * (index - matchups.index(i) - 1)
                ) + i.rooms.index(j)
                if continued is True:
                    try_num = -1000
                if check < try_num:
                    continued = True
                    continue
                unused_rooms.remove(str(j))
                i.room = str(j)
                break
    return matchups


def check_matchups(matchups):
    matchups.reverse()
    while True:
        run_counter = 0
        for i in matchups:
            try_num = 1
            while i.room is None:
                global TIMEOUT
                TIMEOUT += 1
                if TIMEOUT > 1000:
                    raise TimeoutError
                matchups.reverse()
                matchups = make_rooms(matchups, matchups.index(i), try_num)
                try_num += 1
                matchups.reverse()
            else:
                TIMEOUT = 0
                run_counter += 1
        if run_counter == len(matchups):
            break
    matchups.reverse()
    for i in matchups:
        for j in i.teams:
            j.rooms.append(i.room)
            for k in i.teams:
                if not k == j:
                    j.opps.append(k)
    return matchups


def print_matchups(matchups):
    clear()
    print ''.join(str(x) for x in ['Round ', ROUND, ' matchups'])
    print '----------------'
    for i in matchups:
        print ''.join(str(x) for x in [
            'Matchup ',
            matchups.index(i)+1,
            ' - Room: ',
            i.room
        ])
        for j in i.teams:
            print ''.join(str(x) for x in [
                'Team ',
                i.teams.index(j)+1,
                ' : ',
                j.name
            ])


def wait_enter():
    wait_string = str(raw_input('Press enter to continue. '))
    return None


def round_results(matchups):
    for i in matchups:
        clear()
        while True:
            try:
                # team1_score = int(raw_input(''.join([
                #     i.teams[0].name,
                #     ' score: '
                # ])))
                team1_score = randint(0, 50)
                break
            except ValueError:
                print 'That wasn\'t a number, try again!'
        while True:
            try:
                # team2_score = int(raw_input(''.join([
                #     i.teams[1].name,
                #     ' score: '
                # ])))
                team2_score = randint(0, 50)
                break
            except ValueError:
                print 'That wasn\'t a number, try again!'
        diff_score = team1_score - team2_score
        i.teams[0].diff += diff_score
        i.teams[1].diff -= diff_score
        if diff_score > 0:
            i.teams[0].wins += 1
            i.teams[1].losses += 1
        else:
            i.teams[0].losses += 1
            i.teams[1].wins += 1
    return matchups


def print_results(teams):
    clear()
    print ''.join(str(x) for x in ['Round ', ROUND, ' results'])
    print '---------------'
    for i in teams:
        print ''.join(str(x) for x in [
            i.name,
            ' - Score Differential: ',
            i.diff,
            ', Wins: ',
            i.wins,
            ', Losses: ',
            i.losses
        ])
        for j in i.rooms:
            print 'Room used:', j
        for j in i.opps:
            print 'Opponent played:', j.name
    wait_enter()


def print_final_results(teams):
    clear()
    final = [teams[0]]
    for i in teams:
        for j in final:
            if i.wins == j.wins:
                if i.diff > j.diff:
                    final.insert(final.index(j), i)
                    break
            if i.wins > j.wins:
                final.insert(final.index(j), i)
                break
        if i not in final:
            final.append(i)
    print 'Team\t\t\tWins\tLosses\tDiff\
        \n--------------------------------------------'
    for i in final:
        print ''.join(str(x) for x in [
            i.name,
            '\t\t\t',
            i.wins,
            '\t',
            i.losses,
            '\t',
            i.diff
        ])
    wait_enter()

ALLOW_TWO_OPPS = True
ALLOW_TWO_ROOMS = True
while True:
    try:
        clear()
        teams = inputs()
        re_rank = -1
        re_num = 0
        re_num_big = 1
        global TIMEOUT
        TIMEOUT = 0
        global ROUND
        ROUND = 1
        for round in range(NUM_ROUNDS):
            matched = False
            while matched is False:
                TIMEOUT += 1
                if TIMEOUT > 100:
                    raise TimeoutError
                try:
                    matchups = init_matchups(
                        teams,
                        re_rank,
                        re_num,
                        re_num_big
                    )
                    matched = True
                except MatchError as error:
                    re_rank = error.rank
                    re_num = error.re_num
                    re_num_big = error.re_num_big
            TIMEOUT = 0
            matchups = make_rooms(matchups, 0, -1000)
            matchups = check_matchups(matchups)
            print_matchups(matchups)
            wait_enter()
            matchups = round_results(matchups)
            print_results(teams)
            re_rank = -1
            re_num = 0
            re_num_big = 1
            ROUND += 1
        print_final_results(teams)
        break
    except TimeoutError:
        '''
        Here, can allow to let multiple rooms/opponents be legal.
        '''
        ALLOW_TWO_OPPS = False
        ALLOW_TWO_ROOMS = False
        continue
    except FailError:
        '''
        Possibly here as well.
        '''
        clear()
        print 'Tournament Failed'
        SystemExit
