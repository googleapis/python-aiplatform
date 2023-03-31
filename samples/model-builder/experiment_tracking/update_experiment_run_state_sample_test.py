# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from experiment_tracking import update_experiment_run_state_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_get_run")
def test_update_experiment_run_state_sample(mock_update_run_state):

    update_experiment_run_state_sample.update_experiment_run_state_sample(
        run_name=constants.EXPERIMENT_RUN_NAME,
        experiment=constants.EXPERIMENT_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
        state=constants.EXPERIMENT_RUN_STATE,
    )

    mock_update_run_state.assert_called_once_with(constants.EXPERIMENT_RUN_STATE)
