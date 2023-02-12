from dataclasses import dataclass
from functools import lru_cache
from typing import List

import pandas as pd

from ab.agent import AgentRevision
from ab.replay import Replay


@dataclass
class ABResult:
    rev_a: AgentRevision
    rev_b: AgentRevision
    replays: List[Replay]

    def __hash__(self) -> int:
        return hash(f"{self.rev_a.revision} {self.rev_b.revision}")

    @lru_cache()
    def get_result_df(self) -> pd.DataFrame:
        result_list = []
        for r in self.replays:
            tie_flag = r.get_result() == "tie"
            win_by_factories_elimination_flag = (
                not tie_flag and r.get_result_by_factories_elimination() is not None
            )
            win_by_lichen_flag = not tie_flag and not win_by_factories_elimination_flag
            result_dict = {
                "replay_file": str(r.path),
                "player_0_hash": r.player_hashes[0],
                "player_1_hash": r.player_hashes[1],
                "seed": r.seed,
                "tie_flag": tie_flag,
                "win_by_factories_elimination_flag": win_by_factories_elimination_flag,
                "win_by_lichen_flag": win_by_lichen_flag,
            }
            for i in range(2):
                player_hash = r.player_hashes[i]
                assert player_hash in (self.rev_a.revision, self.rev_b.revision)
                player_revision = "a" if player_hash == self.rev_a.revision else "b"
                result_dict.update(
                    {
                        f"{player_revision}_final_n_lichen": r.get_final_n_lichen()[i],
                        f"{player_revision}_final_n_factories": r.get_final_n_factories()[
                            i
                        ],
                        f"{player_revision}_win_flag": (
                            r.get_winner_hash() == r.player_hashes[i]
                        ),
                    }
                )
            result_list.append(result_dict)
        return pd.DataFrame(result_list)
