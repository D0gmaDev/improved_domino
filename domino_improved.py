"""
Par D0gma_
> ipt-activite-dominos
"""

import random


class Domino:

    def __init__(self, i: int, j: int) -> None:
        self.domino = (i, j)

    def get(self, index: int) -> int:
        return self.domino[index]

    def points(self) -> int:
        return sum(self.domino)

    def inverse(self):
        return Domino(self.domino[1], self.domino[0])

    def __str__(self) -> str:
        return f"({self.domino[0]}|{self.domino[1]})"

    def __repr__(self) -> str:
        return f"({self.domino[0]}|{self.domino[1]})"


class Deck:

    def __init__(self, ensemble: list[Domino]) -> None:
        self.ensemble = ensemble

    def size(self) -> int:
        return len(self.ensemble)

    def total_points(self) -> int:
        return sum([domino.points() for domino in self.ensemble])

    def index_of(self, domino: Domino) -> int:
        return self.ensemble.index(domino)

    def index_of_max(self) -> int:
        index, top_domino_points = 0, self.ensemble[0].points()

        for i, domino in enumerate(self.ensemble):
            points = domino.points()
            if points > top_domino_points:
                top_domino_points = points
                index = i
        return index

    def get_max_with_index(self) -> tuple[int, Domino]:
        index = self.index_of_max()
        return index, self.ensemble[index]

    def max(self) -> Domino:
        return self.get_max_with_index()[1]

    def legal_moves(self, face: int) -> list[Domino]:
        return [domino for domino in self.ensemble if domino.get(0) == face or domino.get(1) == face]

    def get_two_ends(self) -> tuple[int, int]:
        return self.ensemble[0].get(0), self.ensemble[len(self.ensemble) - 1].get(1)

    def is_a_train(self) -> bool:
        for i in range(len(self.ensemble) - 1):
            if self.ensemble[i].get(1) != self.ensemble[i + 1].get(0):
                return False
        return True

    def remove_domino(self, i: int) -> None:
        self.ensemble[i] = self.ensemble[len(self.ensemble) - 1]
        self.ensemble.pop()

    def pioche(self, n: int) -> list[Domino]:
        return [self.ensemble.pop(random.randrange(0, len(self.ensemble))) for _ in range(n)]  # indice muet

    def get_highest_legal_domino(self, face: int) -> tuple[int, Domino]:
        moves = self.legal_moves(face)
        return (-1, Domino(-1, -1)) if len(moves) == 0 else Deck(moves).get_max_with_index()

    def __str__(self) -> str:
        return str(self.ensemble)


class Game:

    def __init__(self, n: int, p: int) -> None:
        self.pioche = Deck([Domino(i, j) for i in range(n) for j in range(i)])
        self.train = Deck(self.pioche.pioche(1))
        self.number_of_players = p
        self.hands = [Deck(self.pioche.pioche(6)) for _ in range(self.number_of_players)]
        self.current_player = 0

    def get_hand(self, player: int) -> Deck:
        return self.hands[player]

    def can_current_player_play(self) -> bool:
        end_1, end_2 = self.train.get_two_ends()
        current_hand = self.get_hand(self.current_player)
        return len(current_hand.legal_moves(end_1)) > 0 or len(current_hand.legal_moves(end_2)) > 0

    def is_finished(self) -> bool:
        for hand in self.hands:
            if len(hand.ensemble) == 0:
                return True
        return False

    def __str__(self) -> str:
        string = f"{'=' * 20} \n \n{self.train} \n \nPioche: {self.pioche}\n "
        for player, hand in enumerate(self.hands):
            string += f"\n{player} | {hand}"

        return string + "\n "


def generate_new_game(n: int, p: int) -> Game:
    assert p * 6 <= n * (n - 1) / 2

    game = Game(n, p)

    max_player, value_max = 0, 0

    for player in range(p):
        player_max = game.get_hand(player).max()
        if player_max.points() > value_max:
            max_player = player
            value_max = player_max.points()
    game.current_player = max_player
    return game


def automatic_play(game: Game, pioche_if_blocked: bool = True) -> bool:
    if game.can_current_player_play():
        hand = game.get_hand(game.current_player)
        end_1, end_2 = game.train.get_two_ends()
        index_left, highest_left = hand.get_highest_legal_domino(end_1)
        index_right, highest_right = hand.get_highest_legal_domino(end_2)

        if highest_left.points() < highest_right.points():
            hand.remove_domino(index_right)
            print(f"Le joueur {game.current_player} pose le domino {highest_right} à droite.")
            game.train.ensemble.append(highest_right if end_2 == highest_right.get(0) else highest_right.inverse())
        else:
            hand.remove_domino(index_left)
            print(f"Le joueur {game.current_player} pose le domino {highest_left} à gauche.")
            game.train.ensemble.insert(0, highest_left if end_1 == highest_left.get(1) else highest_left.inverse())

        assert game.train.is_a_train()  # for debugging purposes only
        return True

    elif pioche_if_blocked:
        if game.pioche.size() == 0:
            print(f"Aucun domino dans la pioche pour {game.current_player}")
            return False
        else:
            new_domino = game.pioche.pioche(1)[0]
            game.get_hand(game.current_player).ensemble.append(new_domino)
            print(f"Le joueur {game.current_player} n'avait rien a jouer, il pioche le domino {new_domino}")
            return automatic_play(game, pioche_if_blocked=False)  # peut poser le domino tiré


def get_penalites(game: Game, p: int) -> list[int]:
    return [game.get_hand(player).total_points() for player in range(p)]


def play_a_game(n: int, p: int) -> list[int]:
    game = generate_new_game(n, p)
    number_of_players = len(game.hands)

    round_without_playing = 0

    game.current_player -= 1
    while not game.is_finished():
        game.current_player = (game.current_player + 1) % number_of_players  # change to next player

        print(game)

        success = automatic_play(game)  # return wether the player has actually played or not

        round_without_playing = 0 if success else round_without_playing + 1

        if round_without_playing >= p:  # cut stuck games if nobody played (pioche vide et personne ne peut jouer)
            break

    print(f"Victoire du joueur {game.current_player}")
    return get_penalites(game, p)


def play_multiple_game(number_of_games: int, number_of_players: int) -> list[int]:
    penalites = [0] * number_of_players

    for i in range(number_of_games):
        game_penalites = play_a_game(10, number_of_players)
        penalites = [sum(x) for x in zip(penalites, game_penalites)]

    print(f" \nPénalités totales après {number_of_games} parties: {penalites}")
    return penalites


def statistics(penalites: list[int]) -> list[int]:
    rank_array = [0] * len(penalites)
    for player, pen in enumerate(penalites):
        rank = 1
        for other_pl, other_pl in enumerate(penalites):
            if other_pl < pen:
                rank += 1
        rank_array[player] = rank
    return rank_array


total_penalites = play_multiple_game(number_of_games=15, number_of_players=4)
print(f"Rangs des joueurs: {statistics(total_penalites)}")
