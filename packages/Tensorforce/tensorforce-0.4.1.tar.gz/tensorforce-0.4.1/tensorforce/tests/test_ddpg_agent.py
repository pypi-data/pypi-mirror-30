# Copyright 2017 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import unittest

from tensorforce.tests.base_agent_test import BaseAgentTest
from tensorforce.agents import DDPGAgent


class TestDDPGAgent(BaseAgentTest, unittest.TestCase):

    agent = DDPGAgent
    config = dict(
        update_mode=dict(
            unit='timesteps',
            batch_size=32,
            frequency=32
        ),
        memory=dict(
            type='replay',
            include_next_states=True,
            capacity=10000
        ),
        optimizer=dict(
            type='adam',
            learning_rate=1e-3
        ),
        critic_optimizer=dict(
            type='adam',
            learning_rate=1e-4
        ),
        critic_network=dict(
            size_t0=64,
            size_t1=64
        ),
        actions_exploration=dict(
            type='ornstein_uhlenbeck',
            mu=0.0,
            sigma=0.3,
            theta=0.15
        ),
        target_sync_frequency=32,
        target_update_weight=0.99
    )

    exclude_bool = True
    exclude_int = True
    exclude_float = False
    exclude_bounded = True
    exclude_multi = True
    exclude_lstm = True  # Until internal management is fixed for ddpg

    # multi_config = dict(
    #     batch_size=64,
    #     optimizer=dict(
    #         type='adam',
    #         learning_rate=0.01
    #     )
    # )
