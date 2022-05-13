import io
import json
from dataclasses import dataclass

import pandas as pd
import requests
import streamlit as st


@dataclass
class Pokemon:
    """
    Class representation of a Pokemon
    """

    name: str
    base_experience: int
    sprite_front_default: str
    sprite_back_default: str
    stats: dict

    @property
    def front_image(self):
        picture_resp = requests.get(self.sprite_front_default)
        in_memory_picture = io.BytesIO(picture_resp.content)
        return in_memory_picture

    @property
    def back_image(self):
        picture_resp = requests.get(self.sprite_back_default)
        in_memory_picture = io.BytesIO(picture_resp.content)
        return in_memory_picture

    @property
    def stats_series(self) -> pd.Series:
        """
        Renders a pokemons stats into a more readable format

        Returns
        -------
        dict
            Rendered dict with all pokmeon fighting stats
        """
        stats_dict = {stat["stat"]["name"]: stat["base_stat"] for stat in self.stats}
        return pd.Series(stats_dict)

    @classmethod
    def from_dict(cls, payload: dict) -> "Pokemon":
        """
        Creates a Pokemon instance from a json payload

        Parameters
        ----------
        payload : dict
            A dictionary of parameters required to create an instance of Pokemon

        Returns
        -------
        Pokemon
            Returns an instance of a Pokemon
        """
        return cls(
            name=payload["name"],
            base_experience=payload["base_experience"],
            sprite_front_default=payload["sprites"]["front_default"],
            sprite_back_default=payload["sprites"]["back_default"],
            stats=payload["stats"],
        )


def load_pokemon(pokemon_name: str) -> dict:
    """
    Loads a pokemon from pokeapi

    Parameters
    ----------
    pokemon_name : str
        Name of the pokemon in lower case

    Returns
    -------
    dict
        The resp from pokeapi
    """
    poke_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/"
    resp = requests.get(poke_url)
    return json.loads(resp.text)


@st.cache
def load_all_pokemons() -> list:
    """
    Get's a list of all pokemons

    Returns
    -------
    list
        List with all pokemon names
    """
    resp = requests.get("https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0").text
    resp_to_json = json.loads(resp)
    return [pokemon["name"] for pokemon in resp_to_json["results"]]


def pokemon_template(pokemon_to_render: Pokemon):
    """
    Renders a simple template for a given pokemon

    Parameters
    ----------
    pokemon_to_render : Pokemon
        The pokemon you want to show in the dashboard
    """
    st.subheader(pokemon_to_render.name)
    st.image([pokemon_to_render.front_image, pokemon_to_render.back_image])
    st.bar_chart(pokemon_to_render.stats_series)


# --------------
# Streamlit app
# --------------
st.title("Online Pokedex")

pokemon_choice = st.sidebar.selectbox("Select Pokemon", load_all_pokemons())

bulbasaur = Pokemon.from_dict(load_pokemon(pokemon_choice))

pokemon_template(bulbasaur)
