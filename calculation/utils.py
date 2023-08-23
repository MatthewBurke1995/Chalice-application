import numpyro
from numpyro.infer import MCMC, NUTS
import numpyro.distributions as dist
import jax.numpy as jnp
from jax import random
from jax._src.array import ArrayImpl

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import json


def save_trace(trace):
    dumped = json.dumps(trace, cls=NumpyEncoder)
    with open('trace.json', 'w') as fp:
        json.dump(dumped, fp)



def generate_trace():
    df = generate_game_data()

    observed_home_goals = df.home_score.values
    observed_away_goals = df.away_score.values
    home_team = df.i_home.values
    away_team = df.i_away.values
    num_teams = 20
    #num_teams = len(df.i_home.unique())

    rng_key = random.PRNGKey(0)
    # Run inference
    kernel = NUTS(model)
    mcmc = MCMC(kernel, num_samples=50, num_warmup=1500)
    mcmc.run(rng_key, observed_home_goals, observed_away_goals, num_teams, home_team, away_team)

    # Get samples
    trace = mcmc.get_samples()
    return trace

    
def generate_game_data() -> pd.DataFrame:
    """
    Get scorelines from wikipedia for current season and transform data into
    1 row per game.
    """

    season_df =pd.read_html("https://en.wikipedia.org/wiki/2023%E2%80%9324_Premier_League")[5]
    season_df.index = season_df.columns[1:]
    del(season_df['Home \ Away'])

    #create dataframe where each row corresponds to one game
    season_df.index = season_df.columns
    rows = []
    for i in season_df.index:
        for c in season_df.columns:
            if i == c: continue
            score = season_df[c][i]
            if str(score) in ['nan', 'a']: continue
            score = [int(row) for row in str(score).split('–')]
            rows.append([i, c, score[0], score[1]])
    df = pd.DataFrame(rows, columns = ['home', 'away', 'home_score', 'away_score'])

    teams = season_df.columns
    teams = pd.DataFrame(teams, columns=['team'])
    teams['i'] = teams.index
    teams.head()

    df = pd.merge(df, teams, left_on='home', right_on='team', how='left')
    df = df.rename(columns = {'i': 'i_home'})
    df = pd.merge(df, teams, left_on='away', right_on='team', how='left')
    df = df.rename(columns = {'i': 'i_away'})
    return df 


def model(observed_home_goals, observed_away_goals, num_teams, home_team, away_team):
    def home_theta(intercept, home_advantage, atts, defs):
        return jnp.exp(intercept + home_advantage + atts[home_team] + defs[away_team])

    def away_theta(intercept, atts, defs):
        return jnp.exp(intercept + atts[away_team] + defs[home_team])

    tau_att = numpyro.sample('tau_att', dist.Gamma(concentration=0.1, rate=0.1))
    tau_def = numpyro.sample('tau_def', dist.Gamma(concentration=0.1, rate=0.1))
    tau_home = numpyro.sample('tau_home', dist.Gamma(concentration=0.1, rate=0.1))

    intercept = numpyro.sample('intercept', dist.Normal(0, 0.1))

    atts = numpyro.sample('atts', dist.Normal(0, tau_att).expand([num_teams]).to_event(1))
    defs = numpyro.sample('defs', dist.Normal(0, tau_def).expand([num_teams]).to_event(1))
    home_advantage = numpyro.sample('home_advantage', dist.Normal(0, tau_home))

    home_theta = home_theta(intercept, home_advantage, atts, defs)
    away_theta = away_theta(intercept, atts, defs)

    numpyro.sample('home_goals', dist.Poisson(home_theta), obs=observed_home_goals)
    numpyro.sample('away_goals', dist.Poisson(away_theta), obs=observed_away_goals)


class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, ArrayImpl):
            return obj.tolist()


if __name__ == "__main__":
    trace = generate_trace()
    save_trace(trace)
