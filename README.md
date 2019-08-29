# task-api
### Golem - application communication interface
This work is in it's alpha stage and under heavy development so the interface may change frequently.

This repository contains the interface that the Golem compatible application should implement as well as constants used by the protocol. The interface and the constants are defined under the `golem_task_api/proto` directory in the [Protocol Buffers](https://developers.google.com/protocol-buffers/) files.

This repository also contains programming language specific packages of the `gRPC` protocol which may be used for concrete implementation. This is for the ease of development of the application but it's not required to use them in the application.
If you don't see a programming language you're interested in, feel free to create an issue or even a pull request and we will add it.

# The API
The API is divided into two independent parts - requestor and provider.

## Requestor
For requestor the app should implement a long running RPC service which implements the `RequestorApp` interface from the proto files. The app should assume it will have access to a single directory (let's call it `work_dir`). Each task will have its own separate working directory under the main `work_dir`. You can assume that for a given `task_id` the first call will always be `CreateTask` and the following directories will exist under `work_dir` and they will be empty:
- `{task_id}`
- `{task_id}/{constants.TASK_INPUTS_DIR}`
- `{task_id}/{constants.SUBTASK_INPUTS_DIR}`
- `{task_id}/{constants.TASK_OUTPUTS_DIR}`
- `{task_id}/{constants.SUBTASK_OUTPUTS_DIR}`

### RPC methods
- `CreateTask`
  - takes two arguments `task_id` and `task_params_json`
  - should treat `{work_dir}/{task_id}` as the working directory for the given task
  - `task_params_json` is a JSON string containing task specific parameters
  - will only be called once with given `task_id`
  - can assume `{task_id}/{constants.TASK_INPUTS_DIR}` contains all the resources provided by task creator
- `NextSubtask`
  - takes one argument `task_id`
  - can assume `CreateTask` was called earlier with the same `task_id`
  - returns `subtask_id` which has to be a string without whitespaces and slashes (`/`) but the same string cannot be returned more than once
  - also returns `subtask_params_json` which is the JSON string containing subtask specific parameters
- `HasPendingSubtasks`
  - takes one argument `task_id`
  - returns a boolean indicating whether there are any more pending subtasks waiting for computation at given moment
  - in case when it returns `true`, the next `NextSubtask` call should return successfully
- `Verify`
  - takes two arguments, `task_id` and `subtask_id` which specify which subtask results should be verified
  - will be called with only valid `task_id` and `subtask_id` values
  - returns a boolean indicating whether results passed the verification or not
  - for successfully verified subtasks it most likely should also perform merging the partial results into the final one
- `DiscardSubtasks`
  - takes two arguments, `task_id` and `subtask_ids`
  - should discard results of given subtasks and any dependent subtasks
  - returns list of subtask IDs that have been discarded
  - in a simple case where subtasks are independent from each other it will return the same list as it received
- `Benchmark`
  - takes no arguments
  - returns a score which indicates how efficient the machine is for this type of tasks
  - shouldn't take much time (preferably less than a minute for medium range machines)
- `Shutdown`
  - takes no arguments
  - should gracefully terminate the service

When the last subtask is successfully verified on the requestor's side, the `work_dir/task_id/constants.TASK_OUTPUTS_DIR` directory should contain all result files and nothing else.

## Provider
Provider app should implement a short-lived RPC service which implements the `ProviderApp` interface from the proto files. Short-lived means that there will be only one request issued per service instance, i.e. the service should shutdown automatically after handling the first and only request.

### RPC commands
- `Compute`
  - gets a single working directory `task_work_dir` to operate on
  - different subtasks of the same task will have the same `task_work_dir`
  - takes `task_id`, `subtask_id`, `subtask_params_json` as arguments
  - can assume the `{task_work_dir}/{constants.SUBTASK_INPUTS_DIR}` directory exists
  - can assume that under `{task_work_dir}/{constants.SUBTASK_INPUTS_DIR}` are the resources specified in the corresponding `NextSubtask` call
  - returns a filepath (relative to the `task_work_dir`) of the result file which will be sent back to the requestor with unchanged name
- `Benchmark`
  - takes no arguments
  - returns a score which indicates how efficient the machine is for this type of tasks
  - shouldn't take much time (preferably less than a minute for medium range machines)
