import json
import subprocess
import tempfile
from os import path

import numpy as np

from gameanalysis import agggen
from gameanalysis import gamegen
from gameanalysis import gamereader
from gameanalysis import matgame
from gameanalysis import paygame
from gameanalysis import utils
from gameanalysis.reduction import deviation_preserving as dpr
from gameanalysis.reduction import hierarchical as hr
from gameanalysis.reduction import twins as tr

# To pass files to some scripts we use tempfile.NamedTemporaryFile and just
# flush it prior to running the scripts. Some tests also use /dev/null. Both of
# these will fail on windows.


DIR = path.dirname(path.realpath(__file__))
GA = path.join(DIR, '..', 'bin', 'ga')
HARD_GAME = path.join(DIR, '..', 'example_games', 'hard_nash.json')
with open(HARD_GAME, 'r') as f:
    HARD_GAME_STR = f.read()
with open(path.join(DIR, '..', 'example_games', 'ugly.nfg'), 'r') as f:
    GAMBIT_STR = f.read()
HARD_GAME_DATA = gamereader.loads(HARD_GAME_STR)
GAME_DATA = gamegen.game([3, 2], [2, 3])
GAME_JSON = GAME_DATA.to_json()
GAME_STR = json.dumps(GAME_JSON)

MATGAME = gamegen.independent_game([2, 3])
MATGAME_STR = json.dumps(MATGAME.to_json())


def run(*cmd, input=''):
    res = subprocess.run((GA,) + cmd, input=input.encode('utf-8'),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = res.stdout.decode('utf-8')
    err = res.stderr.decode('utf-8')
    return not res.returncode, out, err


def test_from_module():
    python = path.join(DIR, '..', 'bin', 'python')
    proc = subprocess.run([python, '-m', 'gameanalysis', '--help'])
    assert not proc.returncode


def test_help():
    assert not run()[0]
    assert not run('--fail')[0]
    success, out, err = run('--help')
    assert success, err
    for cmd in (line.split()[0] for line in out.split('\n')
                if line.startswith('    ') and line[4] != ' '):
        success, _, err = run(cmd, '--help')
        assert success, err


def test_dominance_1():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('dom', '-i', game.name)
    assert success, err
    game = gamereader.loads(out)
    assert game == GAME_DATA


def test_dominance_2():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('dom', '-i', game.name, '-s')
    assert success, err
    assert json.loads(out) == GAME_JSON['strategies']


def test_dominance_3():
    success, _, err = run('dom', '-cweakdom', '-o/dev/null', input=GAME_STR)
    assert success, err


def test_dominance_4():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('dom', '-cstrictdom', '-i', game.name)
    assert success, err
    gamereader.loads(out)


def test_dominance_5():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('dom', '-cneverbr', '-i', game.name)
    assert success, err
    gamereader.loads(out)


def test_dominance_6():
    '''Test dom works for non Games'''
    with tempfile.NamedTemporaryFile('w') as game:
        json.dump(MATGAME.to_json(), game)
        game.flush()
        success, _, err = run('dom', '-cweakdom',
                              '-o/dev/null', '-i', game.name)
    assert success, err


def test_gamegen_1():
    assert not run('gen')[0]
    assert not run('gen', 'ursym')[0]
    success, _, err = run('gen', 'uzs', '6', '-n', '-o/dev/null')
    assert success, err


def test_gamegen_2():
    success, out, err = run('gen', 'ursym', '3:4,4:3')
    assert success, err
    gamereader.loads(out)


def test_gamegen_3():
    success, out, err = run(
        'gen', 'noise', '-d', 'uniform', '-w', '1.5', '-s', '5',
        input=GAME_STR)
    assert success, err
    gamereader.loads(out)


def test_gamegen_4():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'gen', 'noise', '-d', 'gumbel', '-w', '1.5', '-s', '5', '-i',
            game.name)
    assert success, err
    gamereader.loads(out)


def test_gamegen_5():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'gen', 'noise', '-d', 'bimodal', '-w', '1.5', '-s', '5', '-i',
            game.name)
    assert success, err
    gamereader.loads(out)


def test_gamegen_noise():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'gen', 'noise', '-d', 'gaussian', '-w', '1.5', '-s', '5', '-i',
            game.name)
    assert success, err
    gamereader.loads(out)


def test_nash_fail():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        assert not run('nash', '-tfail', '-i', game.name)[0]

    success, _, err = run('nash', input=GAME_STR)
    assert success, err


def test_nash_options():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, _, err = run(
            'nash', '-i', game.name, '-o/dev/null', '-r1e-2', '-d1e-2',
            '-c1e-7', '-x100', '-s1e-2', '-m5', '-n', '-p1')
    assert success, err


def test_nash_pure():
    success, out, err = run('nash', '-tpure', '-i', HARD_GAME)
    assert success, err
    assert any(  # pragma: no branch
        np.all(HARD_GAME_DATA.profile_from_json(prof) ==
               [4, 2, 0, 0, 0, 1, 0, 0, 0])
        for prof in json.loads(out))


def test_nash_prof():
    success, out, err = run('nash', '-tmin-reg-prof', '-i', HARD_GAME)
    assert success, err
    assert any(  # pragma: no branch
        np.all(HARD_GAME_DATA.profile_from_json(prof) ==
               [4, 2, 0, 0, 0, 1, 0, 0, 0])
        for prof in json.loads(out))


def test_nash_grid():
    success, out, err = run('nash', '-tmin-reg-grid', '-i', HARD_GAME)
    assert success, err
    assert any(  # pragma: no branch
        np.allclose(HARD_GAME_DATA.mixture_from_json(
            mix), [0, 1, 0, 0, 0, 1, 0, 0, 0])
        for mix in json.loads(out))


def test_nash_pure_one():
    with tempfile.NamedTemporaryFile('w') as game:
        sgame = gamegen.rock_paper_scissors()
        json.dump(sgame.to_json(), game)
        game.flush()
        success, _, err = run('nash', '-tpure', '--one', '-i', game.name)
        assert success, err


def test_nash_mat():
    '''Test nash works with non Game'''
    with tempfile.NamedTemporaryFile('w') as game:
        json.dump(MATGAME.to_json(), game)
        game.flush()
        success, _, err = run('nash', '-o/dev/null', '-i', game.name)
    assert success, err


def test_payoff_pure():
    with tempfile.NamedTemporaryFile('w') as pure:
        prof = [{
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 6},
            'hft': {'noop': 1}}]
        json.dump(prof, pure)
        pure.flush()
        success, _, err = run('pay', '-i', HARD_GAME, pure.name, '-o/dev/null')
        assert success, err

        success, out, err = run(
            'pay', pure.name, '-twelfare', input=HARD_GAME_STR)
        assert success, err
        assert np.isclose(json.loads(out)[0], -315.4034577992763)


def test_payoff_mixed():
    with tempfile.NamedTemporaryFile('w') as mixed:
        prof = [{
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 1},
            'hft': {'noop': 1}}]
        json.dump(prof, mixed)
        mixed.flush()
        success, _, err = run('pay', '-i', HARD_GAME,
                              mixed.name, '-o/dev/null')
        assert success, err

        success, out, err = run(
            'pay', mixed.name, '-twelfare', input=HARD_GAME_STR)
        assert success, err
        assert np.isclose(json.loads(out)[0], -315.4034577992763)


def test_payoff_pure_single():
    with tempfile.NamedTemporaryFile('w') as pure:
        prof = {
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 6},
            'hft': {'noop': 1}}
        json.dump(prof, pure)
        pure.flush()
        success, out, err = run('pay', '-i', HARD_GAME, pure.name)
        assert success, err
        assert np.allclose(HARD_GAME_DATA.payoff_from_json(json.loads(out)[0]),
                           [0, -52.56724296654605, 0, 0, 0, 0, 0, 0, 0])


def test_payoff_pure_string():
    # Singleton payoff as string
    prof = {
        'background': {
            'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 6},
        'hft': {'noop': 1}}
    profstr = json.dumps(prof)
    success, out, err = run('pay', '-i', HARD_GAME, profstr)
    assert success, err
    assert np.allclose(HARD_GAME_DATA.payoff_from_json(json.loads(out)[0]),
                       [0, -52.56724296654605, 0, 0, 0, 0, 0, 0, 0])


def test_reduction_1():
    success, out, err = run('red', 'background:2;hft:1', input=HARD_GAME_STR)
    assert success, err
    game = gamereader.loads(out)
    assert game == dpr.reduce_game(HARD_GAME_DATA, [2, 1])


def test_reduction_3():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('red', '-thr', '-s', '2,1', '-i', game.name)
    assert success, err
    game = gamereader.loads(out)
    assert game == hr.reduce_game(GAME_DATA, [2, 1])


def test_reduction_4():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('red', '-ttr', '-i', game.name)
    assert success, err
    game = gamereader.loads(out)
    assert game == tr.reduce_game(GAME_DATA)


def test_reduction_5():
    '''Test identity reduction'''
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run('red', '-tidr', '-i', game.name)
    assert success, err
    game = gamereader.loads(out)
    assert game == paygame.game_copy(GAME_DATA)


def test_reduction_6():
    '''Test that reduction works for non Games'''
    with tempfile.NamedTemporaryFile('w') as game:
        json.dump(MATGAME.to_json(), game)
        game.flush()
        success, out, err = run('red', '-tidr', '-i', game.name)
        assert success, err
    gamereader.loads(out)


def test_regret_pure():
    with tempfile.NamedTemporaryFile('w') as pure:
        prof = {
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 6},
            'hft': {'noop': 1}}
        json.dump([prof], pure)
        pure.flush()
        success, out, err = run('reg', '-i', HARD_GAME, pure.name)
        assert success, err
        assert np.isclose(json.loads(out)[0], 7747.618428)

        success, out, err = run(
            'reg', pure.name, '-tgains', input=HARD_GAME_STR)
        assert success, err
        dev_pay = json.loads(out)[0]
        for role, strats in dev_pay.items():
            prof_strats = prof[role]
            assert prof_strats.keys() == strats.keys()
            role_strats = set(
                HARD_GAME_DATA.strat_names[HARD_GAME_DATA.role_index(role)])
            for strat, dev_strats in strats.items():
                rstrats = role_strats.copy()
                rstrats.remove(strat)
                assert rstrats == dev_strats.keys()


def test_regret_mixed():
    with tempfile.NamedTemporaryFile('w') as mixed:
        prof = [{
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 1},
            'hft': {'noop': 1}}]
        json.dump(prof, mixed)
        mixed.flush()
        success, out, err = run('reg', '-i', HARD_GAME, mixed.name)
        assert success, err
        assert np.isclose(json.loads(out)[0], 7747.618428)

        success, out, err = run('reg', mixed.name, '-tgains', '-i', HARD_GAME)
        assert success, err
        assert np.allclose(HARD_GAME_DATA.payoff_from_json(json.loads(out)[0]),
                           [581.18996992, 0., 0., 4696.19261, 3716.207196,
                            7747.618428, 4569.842172, 4191.665254,
                            4353.146694])


def test_regret_single():
    with tempfile.NamedTemporaryFile('w') as pure:
        prof = {
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 6},
            'hft': {'noop': 1}}
        json.dump(prof, pure)
        pure.flush()
        success, out, err = run('reg', '-i', HARD_GAME, pure.name)
        assert success, err
        assert np.isclose(json.loads(out)[0], 7747.618428)


def test_restriction_detect():
    success, out, err = run('rest', '-nd', '-i', HARD_GAME)
    assert success, err
    assert HARD_GAME_DATA.restriction_from_json(json.loads(out)[0]).all()


def test_restriction_extract_1():
    success, out, err = run(
        'rest', '-n', '-t',
        'background:markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9;'
        'hft:noop', '-s', '0,3,4', '-i', HARD_GAME)
    assert success, err

    expected = {utils.hash_array([False,  True,  True, False, False, False,
                                  False, False, False]),
                utils.hash_array([True, False, False,  True,  True, False,
                                  False, False, False])}
    assert {utils.hash_array(HARD_GAME_DATA.restriction_from_json(s))
            for s in json.loads(out)} == expected


def test_restriction_extract_2():
    with tempfile.NamedTemporaryFile('w') as sub, \
            tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        rest = [False, True, True, True, False]
        json.dump([GAME_DATA.restriction_to_json(rest)], sub)
        sub.flush()
        success, out, err = run('rest', '-i', game.name, '-f', sub.name)
        assert success, err
        game = gamereader.loadj(json.loads(out)[0])
        assert game == GAME_DATA.restrict(rest)


def test_analysis_output():
    success, out, err = run('analyze', input=GAME_STR)
    assert success, err
    start = '''Game Analysis
=============
Game:
    Roles: r0, r1
    Players:
        3x r0
        2x r1
    Strategies:
        r0:
            s0
            s1
        r1:
            s2
            s3
            s4
payoff data for 24 out of 24 profiles'''
    assert out.startswith(start)
    assert 'Social Welfare\n--------------' in out
    assert 'Maximum social welfare profile:' in out
    assert 'Maximum "r0" welfare profile:' in out
    assert 'Maximum "r1" welfare profile:' in out
    assert 'Equilibria\n----------' in out
    assert 'No-equilibria Subgames\n----------------------' in out
    assert ('Unconfirmed Candidate Equilibria\n'
            '--------------------------------') in out
    assert ('Unexplored Best-response Subgames\n'
            '---------------------------------') in out
    assert 'Json Data\n=========' in out


def test_analysis_dpr():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'analyze', '-i', game.name, '--restrictions', '--dominance',
            '--dpr', 'r0:3;r1:2', '-p1', '--dist-thresh', '1e-3', '-r1e-3',
            '-t1e-3', '--rand-restarts', '0', '-m10000', '-c1e-8')
    assert success, err
    assert 'With deviation preserving reduction: r0:3 r1:2' in out


def test_analysis_hr():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'analyze', '-i', game.name, '--hr', 'r0:3;r1:2', '-p1')
    assert success, err
    assert 'With hierarchical reduction: r0:3 r1:2' in out


def test_analysis_equilibria():
    profiles = [
        # Complete deviations but unexplored
        [4, 0, 0, 0, 0],
        [3, 1, 0, 0, 0],
        [3, 0, 1, 0, 0],
        [3, 0, 0, 1, 0],
        [3, 0, 0, 0, 1],
        # Deviating restriction also explored
        [0, 4, 0, 0, 0],
        [0, 3, 1, 0, 0],
        [0, 2, 2, 0, 0],
        [0, 1, 3, 0, 0],
        [0, 0, 4, 0, 0],
        # Deviations
        [1, 3, 0, 0, 0],
        [1, 2, 1, 0, 0],
        [1, 1, 2, 0, 0],
        [1, 0, 3, 0, 0],
        [0, 3, 0, 1, 0],
        [0, 2, 1, 1, 0],
        [0, 1, 2, 1, 0],
        [0, 0, 3, 1, 0],
        [0, 3, 0, 0, 1],
        [0, 2, 1, 0, 1],
        [0, 1, 2, 0, 1],
        [0, 0, 3, 0, 1],
        # Deviating restriction
        [0, 2, 0, 2, 0],
        [0, 1, 0, 3, 0],
        [0, 0, 0, 4, 0],
    ]
    payoffs = [
        # Complete deviations but unexplored
        [4, 0, 0, 0, 0],
        [4, 1, 0, 0, 0],
        [4, 0, 1, 0, 0],
        [4, 0, 0, 1, 0],
        [4, 0, 0, 0, 0],
        # Deviating restriction also explored
        [0, 1, 0, 0, 0],
        [0, 1, 4, 0, 0],
        [0, 1, 4, 0, 0],
        [0, 1, 4, 0, 0],
        [0, 0, 4, 0, 0],
        # Deviations
        [1, 3, 0, 0, 0],
        [1, 2, 1, 0, 0],
        [1, 1, 2, 0, 0],
        [1, 0, 3, 0, 0],
        [0, 3, 0, 5, 0],
        [0, 2, 1, 5, 0],
        [0, 1, 2, 5, 0],
        [0, 0, 3, 5, 0],
        [0, 3, 0, 0, 0],
        [0, 2, 1, 0, 0],
        [0, 1, 2, 0, 0],
        [0, 0, 3, 0, 0],
        # Deviating restriction
        [0, 2, 0, 2, 0],
        [0, 1, 0, 3, 0],
        [0, 0, 0, 4, 0],
    ]
    game = paygame.game([4], [5], profiles, payoffs)
    game_str = json.dumps(game.to_json())

    success, out, err = run('analyze', '-sd', input=game_str)
    assert success, err
    assert 'Found 1 dominated strategy' in out
    assert 'Found 1 unconfirmed candidate' in out
    assert 'Found 1 unexplored best-response restricted game' in out


def test_analysis_dup_equilibria():
    # Two restrictions, but dominated, so identical equilibria
    profiles = [
        [2, 0, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 2, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 2, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 0, 2],
    ]
    payoffs = [
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
    ]
    game = paygame.game(2, 4, profiles, payoffs)
    game_str = json.dumps(game.to_json())

    success, out, err = run('analyze', '-s', input=game_str)
    assert success, err
    assert 'Found 2 maximal complete restricted games' in out


def test_analysis_dev_explored():
    # Beneficial deviation to an already explored restriction
    profiles = [
        [2, 0, 0, 0],
        [1, 1, 0, 0],
        [1, 0, 1, 0],
        [0, 2, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 2, 0],
        [0, 1, 0, 1],
        [0, 0, 1, 1],
        [0, 0, 0, 2],
    ]
    payoffs = [
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
    ]
    game = paygame.game(2, 4, profiles, payoffs)
    game_str = json.dumps(game.to_json())

    success, out, err = run('analyze', '-s', input=game_str)
    assert success, err
    assert 'Found no unexplored best-response restricted games' in out


def test_analysis_no_data():
    game = paygame.game([2], [2], [[1, 1]], [[5, float('nan')]])
    game_str = json.dumps(game.to_json())

    success, out, err = run('analyze', '-s', input=game_str)
    assert success, err
    assert 'There was no profile with complete payoff data' in out
    assert 'Found no complete restricted games' in out


def test_analysis_no_eqa():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, out, err = run(
            'analyze', '-i', game.name, '--restrictions', '--dominance',
            '--dpr', 'r0:3;r1:2', '-p1', '-r0', '-m0')
    assert success, err
    assert 'Found no equilibria' in out
    assert 'Found 1 no-equilibria restricted game' in out


def test_learning_output():
    success, out, err = run('learning', input=GAME_STR)
    assert success, err
    start = '''Game Learning
=============
RbfGpGame:
    Roles: r0, r1
    Players:
        3x r0
        2x r1
    Strategies:
        r0:
            s0
            s1
        r1:
            s2
            s3
            s4
'''
    assert out.startswith(start)
    assert 'Equilibria\n----------' in out
    assert 'Json Data\n=========' in out


def test_learning_args():
    with tempfile.NamedTemporaryFile('w') as game:
        game.write(GAME_STR)
        game.flush()
        success, _, err = run(
            'learning', '-i', game.name, '-o/dev/null', '-p1', '--dist-thresh',
            '1e-3', '-r1e-3', '-t1e-3', '--rand-restarts', '0', '-m10000',
            '-c1e-8')
        assert success, err


def test_learning_no_eqa():
    data = agggen.congestion(10, 3, 1)
    with tempfile.NamedTemporaryFile('w') as game:
        json.dump(data.to_json(), game)
        game.flush()
        success, out, err = run('learning', '-i', game.name, '-m0', '-r0')
    assert success, err
    assert 'Found no equilibria' in out


def test_boot_1():
    with tempfile.NamedTemporaryFile('w') as mixed, \
            tempfile.NamedTemporaryFile('w') as game:
        sgame = gamegen.samplegame([2, 3], [4, 3], 0.05)
        json.dump(sgame.to_json(), game)
        game.flush()

        profs = [sgame.profile_to_json(sgame.uniform_mixture())]
        json.dump(profs, mixed)
        mixed.flush()

        run('boot', '-i', game.name, mixed.name, '-o/dev/null')


def test_boot_2():
    with tempfile.NamedTemporaryFile('w') as mixed:
        sgame = gamegen.samplegame([2, 3], [4, 3], 0.05)
        game_str = json.dumps(sgame.to_json())

        profs = [sgame.profile_to_json(sgame.random_profile())]
        json.dump(profs, mixed)
        mixed.flush()

        success, out, err = run(
            'boot', mixed.name, '-tsurplus', '--processes', '1', '-n21', '-p',
            '5', '-p', '95', input=game_str)
        assert success, err
        data = json.loads(out)
        assert all(j.keys() == {'5', '95', 'mean'} for j in data)
        assert all(j['5'] <= j['95'] for j in data)


def test_boot_3():
    with tempfile.NamedTemporaryFile('w') as mixed:
        sgame = gamegen.samplegame([2, 3], [4, 3], 0.05)
        game_str = json.dumps(sgame.to_json())

        profs = [sgame.profile_to_json(sgame.random_profile())]
        json.dump(profs, mixed)
        mixed.flush()

        success, out, err = run(
            'boot', mixed.name, '-tsurplus', '--processes', '1', '-n21',
            input=game_str)
        assert success, err
        data = json.loads(out)
        expected = {'mean'}.union(set(map(str, range(0, 101, 5))))
        assert all(j.keys() == expected for j in data)
        assert all(j['5'] <= j['95'] for j in data)


def test_samp_restriction():
    success, out, err = run(
        'samp', '-i', HARD_GAME, 'restriction', '-p', '0.5')
    assert success, err
    sub = HARD_GAME_DATA.restriction_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_restriction(sub)


def test_samp_mix():
    success, out, err = run('samp', '-i', HARD_GAME, 'mix', '-a', '0.5')
    assert success, err
    sub = HARD_GAME_DATA.mixture_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_mixture(sub)


def test_samp_sparse_mix():
    success, out, err = run('samp', '-i', HARD_GAME, 'mix', '-a', '0.5', '-s')
    assert success, err
    sub = HARD_GAME_DATA.mixture_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_mixture(sub)


def test_samp_sparse_mix_prob():
    success, out, err = run('samp', '-i', HARD_GAME, 'mix', '-a', '0.5', '-s',
                            '0.5')
    assert success, err
    sub = HARD_GAME_DATA.mixture_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_mixture(sub)


def test_samp_prof():
    success, out, err = run('samp', '-i', HARD_GAME, 'prof')
    assert success, err
    sub = HARD_GAME_DATA.profile_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_profile(sub)


def test_samp_prof_alpha():
    success, out, err = run('samp', '-i', HARD_GAME, 'prof', '-a', '0.5')
    assert success, err
    sub = HARD_GAME_DATA.profile_from_json(json.loads(out))
    assert HARD_GAME_DATA.is_profile(sub)


def test_samp_prof_mix():
    with tempfile.NamedTemporaryFile('w') as mixed:
        prof = {
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 1},
            'hft': {'noop': 1}}
        json.dump(prof, mixed)
        mixed.flush()
        success, out, err = run('samp', '-i', HARD_GAME, 'prof', '-m',
                                mixed.name)
        assert success, err
        prof = HARD_GAME_DATA.profile_from_json(json.loads(out))
        assert HARD_GAME_DATA.is_profile(prof)


def test_samp_prof_error():
    with tempfile.NamedTemporaryFile('w') as mixed:
        prof = {
            'background': {
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 1},
            'hft': {'noop': 1}}
        json.dump(prof, mixed)
        mixed.flush()
        success, out, err = run('samp', '-i', HARD_GAME, 'prof', '-a', '0.5',
                                '-m', mixed.name)
        assert not success


def test_samp_seed():
    with tempfile.NamedTemporaryFile('w') as mixed:
        prof = {
            'background': {
                'markov:rmin_30000_rmax_30000_thresh_0.001_priceVarEst_1e6':
                0.5,
                'markov:rmin_500_rmax_1000_thresh_0.8_priceVarEst_1e9': 0.5},
            'hft': {'noop': 1}}
        json.dump(prof, mixed)
        mixed.flush()
        success, out1, err1 = run(
            'samp', '-i', HARD_GAME, '-n', '100', '--seed', '1234', 'prof',
            '-m', mixed.name)
        assert success, err1
        for line in out1[:-1].split('\n'):
            prof = HARD_GAME_DATA.profile_from_json(json.loads(line))
            assert HARD_GAME_DATA.is_profile(prof)

        # Setting seed produces identical output
        success, out2, err2 = run(
            'samp', '-i', HARD_GAME, '-n', '100', '--seed', '1234', 'prof',
            '-m', mixed.name)
        assert success, err2
        assert out1 == out2

        # Not setting it causes failure
        # This can technically fail, but the probability is very small
        success, out3, err3 = run(
            'samp', '-i', HARD_GAME, '-n', '100', 'prof', '-m', mixed.name)
        assert success, err3
        assert out1 != out3


def test_conv_game_empty():
    success, _, err = run('conv', '-o/dev/null', 'empty', input=GAME_STR)
    assert success, err


def test_conv_game_game():
    success, _, err = run('conv', '-o/dev/null', 'game', input=GAME_STR)
    assert success, err


def test_conv_game_sgame():
    success, _, err = run(
        'conv', '-o/dev/null', 'samp', input=GAME_STR)
    assert success, err


def test_conv_game_mat():
    success, _, err = run('conv', '-o/dev/null', 'mat', input=GAME_STR)
    assert success, err


def test_conv_game_str():
    success, _, err = run('conv', '-o/dev/null', 'str', input=GAME_STR)
    assert success, err


def test_conv_game_gambit():
    success, _, err = run('conv', '-o/dev/null', 'gambit', input=GAME_STR)
    assert success, err


def test_conv_game_norm():
    success, out, err = run(
        'conv', 'norm', input=GAME_STR)
    assert success, err
    game = gamereader.loads(out)
    assert np.allclose(game.min_role_payoffs(), 0)
    assert np.all(np.isclose(game.max_role_payoffs(), 1) |
                  np.isclose(game.max_role_payoffs(), 0))


def test_conv_mat_empty():
    success, _, err = run(
        'conv', '-o/dev/null', 'empty', input=MATGAME_STR)
    assert success, err


def test_conv_mat_game():
    success, _, err = run('conv', '-o/dev/null', 'game', input=MATGAME_STR)
    assert success, err


def test_conv_mat_sgame():
    success, _, err = run(
        'conv', '-o/dev/null', 'samp', input=MATGAME_STR)
    assert success, err


def test_conv_mat_mat():
    success, _, err = run(
        'conv', '-o/dev/null', 'mat', input=MATGAME_STR)
    assert success, err


def test_conv_mat_str():
    success, _, err = run(
        'conv', '-o/dev/null', 'str', input=MATGAME_STR)
    assert success, err


def test_conv_mat_gambit():
    success, _, err = run(
        'conv', '-o/dev/null', 'gambit', input=MATGAME_STR)
    assert success, err


def test_conv_gambit_mat():
    success, _, err = run(
        'conv', '-o/dev/null', 'mat', input=GAMBIT_STR)
    assert success, err


def test_conv_gambit_game():
    success, _, err = run(
        'conv', '-o/dev/null', 'game', input=GAMBIT_STR)
    assert success, err


def test_conv_mat_norm():
    success, out, err = run(
        'conv', 'norm', input=MATGAME_STR)
    assert success, err
    game = gamereader.loads(out)
    assert np.allclose(game.min_role_payoffs(), 0)
    assert np.all(np.isclose(game.max_role_payoffs(), 1) |
                  np.isclose(game.max_role_payoffs(), 0))


def test_conv_game_mat_inv():
    success, out, err = run('conv', 'matgame', input=GAME_STR)
    assert success, err
    success, out, err = run('conv', 'game', input=out)
    assert success, err
    game = gamereader.loads(out)
    assert game == paygame.game_copy(matgame.matgame_copy(GAME_DATA))


def test_conv_game_gambit_inv():
    success, out, err = run('conv', 'gambit', input=GAME_STR)
    assert success, err
    success, out, err = run('conv', 'game', input=out)
    assert success, err
    game = gamereader.loads(out)
    assert game == paygame.game_copy(matgame.matgame_copy(GAME_DATA))


def test_conv_mat_game_inv():
    success, out, err = run('conv', 'game', input=MATGAME_STR)
    assert success, err
    success, out, err = run('conv', 'matgame', input=out)
    assert success, err
    game = gamereader.loads(out)
    assert game == MATGAME


def test_conv_mat_gambit_inv():
    success, out, err = run('conv', 'gambit', input=MATGAME_STR)
    assert success, err
    success, out, err = run('conv', 'matgame', input=out)
    assert success, err
    game = gamereader.loads(out)
    assert game == MATGAME
