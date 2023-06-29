A Reinforcement Learning Method Based on Information Evaluation


Abstract
The success of current machine learning techniques is mainly attributed to a large amount of independently and identically distributed (i.i.d.) training data. However, due to the inability to effectively understand causal relationships, they exhibit poor environmental transferability. In the process of understanding and transforming the world, humans are good at summarizing and abstracting knowledge from the environment. This abstract knowledge can easily adapt to environmental changes, greatly improving the scope of knowledge application. In order to imitate this abstract ability of humans, this paper proposes a model-based reinforcement learning method that builds a knowledge graph model of the environment, continuously assumes the correlation between various information in the environment, and observes the size of the gain brought by various hypotheses in interaction, so as to continuously optimize the model and mine the knowledge graph of the environment. I tested it in a self-made grid world, and the experimental results show that the modeling results of the model can guide the agent to make correct decisions in different changes of the game, and it is easy to transfer its modeling results to similar environments.

Citation
Causal relationship learning has always been a milestone challenge in the field of artificial intelligence. Humans can easily infer the causal relationship between different elements through intuition without explicit guidance. Most of the current machine learning techniques are quite successful because they rely on large-scale pattern recognition of appropriately collected i.i.d. data. However, in reality, because it is impossible to consider and control all factors in the training data, the distribution often changes. To make machine learning models work outside the i.i.d. domain, it is necessary not only to learn the statistical correlations between variables, but also to learn potential causal models [1].

The paper argues that adding causal relationship models to supervised learning has significant limitations. First, the added causal relationship model cannot evaluate and optimize the causal relationship itself. Secondly, the domain knowledge information of supervised learning is one-sided, and only those few causal relationships in the domain knowledge are difficult to further compare and summarize new, higher-order relationships from a large number of relationships.

Using reinforcement learning can effectively solve these two shortcomings. First, reinforcement learning obtains experimental results through continuous interaction with the environment, theoretically, its data sample is infinite. Second, reinforcement learning can combine specific search strategies to prioritize the direction that the policy considers important, thereby improving the sample efficiency of reinforcement learning.

Third, in the reinforcement learning algorithm in this paper, the search strategy will continuously optimize based on the expanding knowledge graph model, so that the sample efficiency can continue to improve in the continuous learning process.


Background:
Markov Decision Process (MDP) is the foundation of current reinforcement learning. Reinforcement learning algorithms consider the exploration process of the machine and the environment as a state-action transition, and the goal is to make a behavioral function or state function converge. This kind of reinforcement learning based on Markov decision process overemphasizes the objectivity of state transition and ignores the subjectivity of decision-making. This makes the reinforcement learning based on it only limited to learning state-action pairs, and does not delve into why this action should be taken in this state.
This article proposes a method that is based on the information observed by the agent, proposes hypotheses about the interrelationships between information, and verifies the correctness of the hypotheses in the environment. This method allows reinforcement learning not only to seek a value function, but its learning goal is to find as many intrinsic relationships in the environment as possible.

Algorithm Introduction:
while True:

Based on the existing information, propose some brand new hypotheses.
Continue to play many rounds and conduct pruning simulations for the hypotheses.
Use Monte Carlo Tree Search (MCTS) to calculate the hit rate of the hypotheses and evaluate the effectiveness of the decision-making behavior of the hypotheses.
If the hit rate is close to random, discard it; if the hit rate is high or low, leave it and conduct further evaluation.
Reverse the low hit rate hypotheses and retain the high ones. Understand the information surrounding effective hypotheses (observe downwards, observe peers, observe upwards).
Based on the existing information, propose many new hypotheses, traverse their surroundings, and summarize the interrelationships between the hypotheses (observe downwards, observe peers, observe upwards). If it is close to the expected payoff of the optimal model, break.
For example, let's consider a scenario where a player earns rewards for eating apples. Observing downwards means that when we observe the proposition "apples can be eaten," we should also observe the sub-propositions of "green apples can be eaten" and "red apples can be eaten" and find that it is true. Observing peers means that when we discover that apples can be eaten, apples belong to the set of fruits, and we should propose hypotheses about whether oranges and bananas can be eaten. Observing upwards means that when a large number of hypotheses are true, we propose hypotheses upwards based on existing experience. For example, we propose the hypothesis of "whether fruits can be eaten."

To demonstrate the good transfer adaptability of this knowledge graph, I simulated it in a Minesweeper game and observed the adaptability of the model by changing the size of the chessboard and the rules of mining.

Minesweeper Game:
This is a Minesweeper game that I created. The rules of the game are that at the beginning of the game, the upper left square displays a number, which represents the number of mines in the up, down, left, and right directions. There is only one mine in each column, and the game ends when all non-mine squares are swept. If you step on a mine, you get a reward of -1. The size of the chessboard can be customized.
Obviously, the more information a player has, the easier it is to pass the game.
Information can be divided into several categories: 1. Information that can be seen on the board. 2. Information that can be inferred from numbers and number combinations. 3. The hidden game rules that there is only one mine in each column can be discovered through multiple simulations.
Using Monte Carlo random simulation, we can calculate the expected reward under the current information level and the marginal expected reward brought by each piece of information. Any useful information that has been repeatedly proved can be stored