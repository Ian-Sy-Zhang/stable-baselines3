class ActionScoringStateMachine:
    def __init__(self, action_sequence, correct_score, incorrect_score, finish_score = 100):
        self.states = self.build_states(action_sequence)
        self.current_state = self.states[0]
        self.correct_score = correct_score
        self.incorrect_score = incorrect_score
        self.finish_score = finish_score
        self.state_action_dict = {
            (2, 2): 'up',
            (2, 1): 'right',
            (3, 1): 'down',
            (3, 2): 'down',
        }

    def build_states(self, action_sequence):
        states = [""]  # 初始状态
        for action in action_sequence:
            states.append(states[-1] + ',' + action if states[-1] else action)
        return states

    def perform_action(self, action):
        next_state_index = self.states.index(self.current_state) + 1
        if next_state_index == len(self.states):
            next_state_index = 0  # 如果当前已经在最后一个状态，那么回到初始状态

        if self.states[next_state_index].endswith(action):
            # 如果动作正确，进入下一个状态并获得正向得分
            self.current_state = self.states[next_state_index]
            if next_state_index == len(self.states) - 1:
                print("COMBO!!!!")
                self.current_state = self.states[0]
                return self.finish_score
            return self.correct_score * next_state_index
        else:
            # 如果动作错误，回到初始状态并获得负向得分
            self.current_state = self.states[0]
            return self.incorrect_score


    # new version of state machine rewarder
    def perform_action2(self, state, action):
        if state in self.state_action_dict.keys():
            if action == self.state_action_dict[state]:
                return 1
            else:
                return -1
        return 0


