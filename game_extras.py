def increase_level(self):
    self.obs_velocity = 0.27
    self.step_velocity = 0.43


def increment_score(self):
    self.score += 1
    self.score_txt = "SCORE: " + str(self.score)


def game_over(self):
    pass

