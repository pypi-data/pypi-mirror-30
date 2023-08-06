from lahman import *
from pitching_leaders import *
from batting_leaders import *
from league_batting_stats import *
from league_pitching_stats import * 
from playerid_lookup import *
from standings import *
from statcast_batter import *
from statcast_pitcher import *
from statcast import *
from team_batting import *
from team_pitching import *
from team_results import *
import sys

sys.stdout = open('/Users/jledoux/Downloads/outputs.txt', 'w')

funcs = [
		"team_batting(1901, 2017)",
		"team_batting(1901, 2017, ind=0)",
		"team_batting(2015)",
		"team_batting(2015,league='al')",
		"team_pitching(1901, 2017)",
		"team_pitching(1901, 2017, ind=0)",
		"team_pitching(2015)",
		"team_pitching(2015, league = 'al')",
		"batting_stats(1901, 2017)",
		"batting_stats(1901, 2017, ind=0)",
		"batting_stats(2015)",
		"batting_stats(2015,league='al')",
		"pitching_stats(2015, league = 'al', qual=1)", # should be same
		"pitching_stats(2015, league = 'al', qual=100)", # should be less rows
		"pitching_stats(1901, 2017)",
		"pitching_stats(1901, 2017, ind=0)",
		"pitching_stats(2015)",
		"pitching_stats(2015, league = 'al')",
		"pitching_stats(2015, league = 'al', qual=1)", # should be same
		"pitching_stats(2015, league = 'al', qual=100)", # should be less rows		
		"schedule_and_record(1911,'NYY')",
		"schedule_and_record(2011,'NYY')",
		"schedule_and_record(1895,'NYY')",
		"standings()",
		"standings(2015)",
		"standings(1977)",
		"standings(1910)",
		"standings(1890)",
		"pitching_stats_range('2017-06-10')",
		"pitching_stats_range('2017-06-10', 2017-08-10')",
		"pitching_stats_range('2017-03-10', 2017-08-10')",
		"pitching_stats_range('2017-03-10', 2017-12-10')",
		"pitching_stats_range('2015-03-10', 2017-08-10')",
		"pitching_stats_bref(2008)",
		"pitching_stats_bref(2017)",
		"bwar_pitch()",
		"bwar_pitch(return_all=True)",
		"batting_stats_range('2017-06-10')",
		"batting_stats_range('2017-06-10', 2017-08-10')",
		"batting_stats_range('2017-03-10', 2017-08-10')",
		"batting_stats_range('2017-03-10', 2017-12-10')",
		"batting_stats_range('2015-03-10', 2017-08-10')",
		"batting_stats_bref(2008)",
		"batting_stats_bref(2017)",
		"bwar_bat()",
		"bwar_bat(return_all=True)",
		"statcast_batter(start_dt= '2016-04-10', end_dt='2016-10-10', player_id = 405395)",
		"statcast_batter(start_dt= '2010-04-10', end_dt='2016-10-10', player_id = 405395)",
		"statcast_pitcher(start_dt= '2016-04-10', end_dt='2016-10-10', player_id = 477132)",
		"statcast_pitcher(start_dt= '2010-04-10', end_dt='2016-10-10', player_id = 477132)",
		"statcast('2010-04-10','2010-04-14')",
		"statcast('2010-04-10','2010-10-14')",
		"statcast('2010-04-10','2012-04-14')",
		"statcast_single_game(263936)",
		"playerid_lookup('kershaw','clayton')",
		"playerid_reverse_lookup([405395,477132])",
		"download_lahman()",
		"teams_half()",
		"teams_franchises()",
		"teams()",
		"series_post()",
		"schools()",
		"salaries()",
		"pitching_post()",
		"pitching()",
		"master()",
		"managers_half()",
		"managers()",
		"home_games()",
		"hall_of_fame()",
		"fielding_post()",
		"fielding_of()",
		"fielding_of_split()",
		"fielding()",
		"college_playing()",
		"batting_post()",
		"batting()",
		"awards_share_players()",
		"awards_share_managers()",
		"awards_players()",
		"awards_managers()",
		"appearances()",
		"all_star_full()",
		"parks()"]

for f in funcs:
	print(f)
	f1 = f + ".shape"
	f2 = f + ".head()"
	try:
		print(eval(f1))
		#exec(f1)
		print(eval(f2))
		#exec(f2)
	except:
		print("{} failed".format(f))



#		